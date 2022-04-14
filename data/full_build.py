from charts_scrape import ChartsScrape
from build_net import BuildNet

def run():
    chartScrape = ChartsScrape()
    chartScrape.run()

    buildNet = BuildNet()
    buildNet.run()

if __name__ == '__main__':
    run()