# GPU-Finder
Searches for GPUs that don't need 8 or 6 pin power, then finds their price and performance rating.

## Requirements
* requests
* BeautifulSoup4

## Usage
Set the price range with the tuple on line 6, then run and wait. It usually takes tens of seconds to run, due to the number of requests. Data is then saved to a CSV named by the price range.

## Acknowledgements
This scapes GPUs from the ![TechPowerUp](https://www.techpowerup.com/gpu-specs/) GPU database, finds pricing on CEX (API from ![@teamplz/CEX-API](https://github.com/teamplz/CEX-API]) and gets performance data from a CSV provided by ![UserBenchmark](https://www.userbenchmark.com/page/developer) (note: this is downloaded to your PC and kept in the same folder as main.py).
