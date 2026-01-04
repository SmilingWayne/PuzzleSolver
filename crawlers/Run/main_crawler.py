from CrawlerFactory import CrawlerFactory
from Core.core import CrawlerConfig

def main():
    # Define configuration
    target = "Doors"
    
    # NOTE:
    #   puzzle_name: The name of dataset saved to repo;
    #   index_url: The url where indices of puzzles can be obtained;
    #   base_url: The direct url where puzzles can be accessed.
    # NOTE: 
    #   Sometimes the puzzle_name is NOT equal to the puzzle name in `index_url`!
    config = CrawlerConfig(
        puzzle_name= f"{target}",
        index_url = f"https://www.janko.at/Raetsel/{target}/index.htm",
        base_url = f"https://www.janko.at/Raetsel/{target}/",
        headless = True,  # Set to False to watch the browser for debugging
        partial_test = False
        # output_dir = './data'
    )
    
    config = CrawlerConfig(
        puzzle_name= f"{target}",
        index_url = f"https://www.janko.at/Raetsel/Tueren/index.htm",
        base_url = f"https://www.janko.at/Raetsel/Tueren/",
        headless = True,  # Set to False to watch the browser for debugging
        partial_test = False # If you wanna check instead of accessing full data, set to True
        # output_dir = './data'
    )
  
    # Instantiate and run
    crawler = CrawlerFactory.get_crawler(target, config)
    crawler.run()

if __name__ == "__main__":
    main()

