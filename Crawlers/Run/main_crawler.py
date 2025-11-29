from AkariCrawler import AkariCrawler

if __name__ == "__main__":
    data = {
        "puzzle_name": "Akari",
        "index_url": "https://www.janko.at/Raetsel/Akari/index.htm",
        "root_url": "https://www.janko.at/Raetsel/Akari/"
    }
    crawler = AkariCrawler(data = data)
    ret = crawler.get_puzzle_indexes()
    # print(ret)
    ret_ = crawler.get_puzzles_from_batch(ret)
    crawler.save_puzzles_to_folder(ret_)
    
    # print(ret['class_sv'], ret['other'])
    
    