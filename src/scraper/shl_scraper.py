"""
SHL Product Catalog Web Scraper

This module scrapes the SHL product catalog to extract Individual Test Solutions.
It navigates through the catalog, filters out Pre-packaged Job Solutions, and
extracts detailed information about each assessment.
"""

import json
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SHLScraper:
    """Scraper for SHL Product Catalog"""
    
    BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
    
    def __init__(self, headless: bool = True):
        """
        Initialize the scraper
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.assessments = []
        
    def setup_driver(self) -> webdriver.Chrome:
        """Set up Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    def extract_duration(self, text: str) -> Optional[int]:
        """
        Extract duration in minutes from text
        
        Args:
            text: Text containing duration information
            
        Returns:
            Duration in minutes or None
        """
        if not text:
            return None
            
        # Look for patterns like "30 minutes", "1 hour", "45-60 minutes"
        patterns = [
            r'(\d+)\s*(?:minute|min)',
            r'(\d+)\s*(?:hour|hr)',
            r'(\d+)-(\d+)\s*(?:minute|min)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if 'hour' in pattern or 'hr' in pattern:
                    return int(match.group(1)) * 60
                elif len(match.groups()) == 2:  # Range
                    return (int(match.group(1)) + int(match.group(2))) // 2
                else:
                    return int(match.group(1))
        
        return None
    
    def scrape_assessment_details(self, url: str) -> Dict:
        """
        Scrape detailed information from an assessment page
        
        Args:
            url: URL of the assessment page
            
        Returns:
            Dictionary containing assessment details
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract details
            details = {
                'url': url,
                'name': '',
                'description': '',
                'test_type': '',
                'duration_minutes': None,
                'skills_measured': [],
                'category': ''
            }
            
            # Extract name
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                details['name'] = title_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = soup.find('div', class_=re.compile(r'description|overview|summary'))
            if not desc_elem:
                desc_elem = soup.find('meta', attrs={'name': 'description'})
                if desc_elem:
                    details['description'] = desc_elem.get('content', '')
            else:
                details['description'] = desc_elem.get_text(strip=True)
            
            # Extract test type (K for Knowledge, P for Personality, etc.)
            test_type_elem = soup.find(text=re.compile(r'Test Type|Type:'))
            if test_type_elem:
                parent = test_type_elem.find_parent()
                if parent:
                    test_type_text = parent.get_text()
                    # Look for single letter codes
                    type_match = re.search(r'\b([KPC])\b', test_type_text)
                    if type_match:
                        details['test_type'] = type_match.group(1)
            
            # Extract duration
            duration_text = soup.get_text()
            details['duration_minutes'] = self.extract_duration(duration_text)
            
            # Extract skills/competencies
            skills_section = soup.find(text=re.compile(r'Skills|Competencies|Measures'))
            if skills_section:
                parent = skills_section.find_parent()
                if parent:
                    skill_items = parent.find_all('li')
                    details['skills_measured'] = [item.get_text(strip=True) for item in skill_items]
            
            return details
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return {'url': url, 'error': str(e)}
    
    def scrape_catalog_page(self, driver: webdriver.Chrome) -> List[str]:
        """
        Extract assessment URLs from catalog page
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            List of assessment URLs
        """
        urls = []
        
        try:
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and parse
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all links to individual assessments
            # Adjust selectors based on actual website structure
            links = soup.find_all('a', href=re.compile(r'/product-catalog/view/'))
            
            for link in links:
                href = link.get('href')
                if href:
                    # Filter out Pre-packaged Job Solutions
                    link_text = link.get_text(strip=True).lower()
                    
                    # Skip if it's a pre-packaged solution
                    if 'solution' in link_text and 'level' in link_text:
                        # These are typically pre-packaged (e.g., "Entry Level Sales Solution")
                        continue
                    
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in urls:
                        urls.append(full_url)
            
            print(f"Found {len(urls)} assessment URLs on current page")
            
        except Exception as e:
            print(f"Error extracting URLs: {str(e)}")
        
        return urls
    
    def scrape_all_assessments(self, max_pages: int = 50) -> List[Dict]:
        """
        Scrape all Individual Test Solutions from the catalog
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of assessment dictionaries
        """
        print("Starting SHL catalog scraping...")
        print(f"Target: At least 377 Individual Test Solutions")
        
        driver = self.setup_driver()
        all_urls = set()
        
        try:
            # Navigate to catalog
            driver.get(self.BASE_URL)
            time.sleep(3)
            
            # Handle any popups/cookies
            try:
                cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
                cookie_btn.click()
                time.sleep(1)
            except:
                pass
            
            # Try to filter to show only Individual Tests
            try:
                # Look for filter options
                filter_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Individual')]")
                if filter_btns:
                    filter_btns[0].click()
                    time.sleep(2)
            except:
                print("No individual test filter found, scraping all...")
            
            # Scrape first page
            page_urls = self.scrape_catalog_page(driver)
            all_urls.update(page_urls)
            
            # Try pagination
            page = 1
            while page < max_pages:
                try:
                    # Look for next button
                    next_btn = driver.find_element(By.XPATH, "//a[contains(text(), 'Next') or contains(@class, 'next')]")
                    if not next_btn.is_displayed() or not next_btn.is_enabled():
                        break
                    
                    next_btn.click()
                    time.sleep(2)
                    page += 1
                    
                    page_urls = self.scrape_catalog_page(driver)
                    all_urls.update(page_urls)
                    
                    print(f"Page {page}: Total URLs collected: {len(all_urls)}")
                    
                except NoSuchElementException:
                    print("No more pages found")
                    break
                except Exception as e:
                    print(f"Pagination error: {str(e)}")
                    break
            
            print(f"\nTotal assessment URLs found: {len(all_urls)}")
            
            # Scrape details for each assessment
            print("\nScraping assessment details...")
            for i, url in enumerate(all_urls, 1):
                print(f"Scraping {i}/{len(all_urls)}: {url}")
                details = self.scrape_assessment_details(url)
                self.assessments.append(details)
                time.sleep(0.5)  # Be polite
            
        finally:
            driver.quit()
        
        # Filter out errored entries
        valid_assessments = [a for a in self.assessments if 'error' not in a]
        print(f"\nSuccessfully scraped {len(valid_assessments)} assessments")
        
        return valid_assessments
    
    def save_to_file(self, output_path: str):
        """
        Save scraped data to JSON file
        
        Args:
            output_path: Path to output file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.assessments, f, indent=2, ensure_ascii=False)
        
        print(f"\nData saved to {output_file}")
        print(f"Total assessments: {len(self.assessments)}")


def main():
    """Main execution function"""
    scraper = SHLScraper(headless=False)  # Set to False to see browser
    
    # Scrape all assessments
    assessments = scraper.scrape_all_assessments(max_pages=20)
    
    # Save to file
    output_path = "data/raw/shl_assessments.json"
    scraper.save_to_file(output_path)
    
    # Print summary
    print("\n" + "="*50)
    print("SCRAPING SUMMARY")
    print("="*50)
    print(f"Total assessments scraped: {len(assessments)}")
    print(f"Target: 377+ Individual Test Solutions")
    print(f"Status: {'✓ SUCCESS' if len(assessments) >= 377 else '✗ INCOMPLETE'}")
    
    if assessments:
        print(f"\nSample assessment:")
        print(json.dumps(assessments[0], indent=2))


if __name__ == "__main__":
    main()
