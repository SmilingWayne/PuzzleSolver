from AkariCrawler import AkariCrawler

if __name__ == "__main__":
    data = {
        "saved_folder": "Akari",
        "index_url": "https://www.janko.at/Raetsel/Fillomino/index.htm"
    }
    crawler = AkariCrawler(data = data)
    ret = crawler.get_puzzle_indexes()
    print(len(ret['class_sv']), len(ret['other']))
    # print(ret['class_sv'], ret['other'])
    
    