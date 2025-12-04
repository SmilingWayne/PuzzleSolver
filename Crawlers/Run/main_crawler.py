from CrawlerFactory import CrawlerFactory

def get_specific_puzzle(target, data):
    crawler = CrawlerFactory.get_crawler(target, data)
    ret = crawler.get_puzzle_indexes()
    ret_ = crawler.get_puzzles_from_batch(ret)
    crawler.save_puzzles_to_folder(ret_)
    print(f"[Done] {target}")

if __name__ == "__main__":
    # Sternenhimmel
    target = "Sternenhimmel"
    data = {
        "puzzle_name": f"{target}",
        "index_url": f"https://www.janko.at/Raetsel/{target}/index.htm",
        "root_url": f"https://www.janko.at/Raetsel/{target}/"
    }
    
    # Used for ununified puzzles
    target = "Kakkuru"
    data = {
        "puzzle_name": f"{target}",
        "index_url": f"https://www.janko.at/Raetsel/Lateinische-Summen/index.htm",
        "root_url": f"https://www.janko.at/Raetsel/Lateinische-Summen/"
    }
    
    
    get_specific_puzzle(target, data)
    
    