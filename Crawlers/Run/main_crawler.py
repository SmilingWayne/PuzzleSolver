from CrawlerFactory import CrawlerFactory

if __name__ == "__main__":
    target = "Str8t"
    data = {
        "puzzle_name": f"{target}",
        "index_url": f"https://www.janko.at/Raetsel/{target}/index.htm",
        "root_url": f"https://www.janko.at/Raetsel/{target}/"
    }
    
    data = {
        "puzzle_name": f"{target}",
        "index_url": f"https://www.janko.at/Raetsel/Straights/index.htm",
        "root_url": f"https://www.janko.at/Raetsel/Straights/"
    }
    
    crawler = CrawlerFactory.get_crawler(target, data)
    ret = crawler.get_puzzle_indexes()
    # print(ret)
    ret_ = crawler.get_puzzles_from_batch(ret)
    crawler.save_puzzles_to_folder(ret_)
    
    # print(ret['class_sv'], ret['other'])
    
    