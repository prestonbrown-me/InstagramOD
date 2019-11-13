from profile_scraper import ProfileScraper
from OverdriveDB import Mongoloid
from MainAutomation import MainAutomation
import credentials

m = Mongoloid()

main_automation = MainAutomation()
main_automation.start()

threads = []
for item in credentials.botlogins:
    scraper = ProfileScraper(item, credentials.botlogins[item], m)
    threads.append(scraper)
    scraper.start()

main_automation.join()
