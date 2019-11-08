from profile_scraper import ProfileScraper
from OverdriveDB import Mongoloid
from MainAutomation import MainAutomation

m = Mongoloid()

logins = {}

# FOR SCRAPER BOTS, ADD THEM INTO THE LOGINS DICTIONARY LIKE SO
# YOU CAN ADD AS MANY AS YOU LIKE
# logins['username'] = 'Password'

main_automation = MainAutomation()
main_automation.start()

threads = []
for item in logins:
    scraper = ProfileScraper(item, logins[item], m)
    threads.append(scraper)
    scraper.start()

threads[0].join()
