from poeninjacrawler import PoENinjaCrawler
from poetradecrawler import PoETradeCrawler
from wikicrawler import WikiCrawler

# myLegacyCrawler = PoETradeCrawler('Legacy')
# myStandardCrawler = PoETradeCrawler('Standard')
# myWikiCrawler = WikiCrawler()

# myLegacyCrawler.parse_all(myWikiCrawler)
# myStandardCrawler.parse_all(myWikiCrawler)


myLegacyCrawler = PoENinjaCrawler('Abyss', 60, 90, 90)
myLegacyCrawler.produce_result_files()
myStandardCrawler = PoENinjaCrawler('Standard', 70, 100, 100)
myStandardCrawler.produce_result_files()
