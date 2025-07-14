# RAG-for-F1-driver

## I - Implementation:

### 1 - Data Scrawling

#### 1.1 - Initialise URLs

- `BASE_URL` at: `https://www.formula1.com`
- Initialise drivers `DRIVER_HREF`: `en/drivers`

#### 1.2 - Initialise HTML reader

- Create function: `get_soup` for transform HTML format to BeautifulSoup4 format

#### 1.3 - Drivers Scraping

##### 1.3.1 - Get Drivers url list

- Step 1: Get drivers slug
- Step 2: Join driver slug with `BASE_URL` and `DRIVER_HREF`
- Step 3: Append to Driver URL list

##### 1.3.2 - Scrape driver data

- Step 1: get HTML soup with `get_soup` for
  - All drivers page
  - Individual driver
  - List of news pages for each driver
  - Each article belonged to driver
- Step 2: Scrape current season's driver statistic with `scrape_driver_statistic()`
- Step 3: Scrape driver biography with `scrape_driver_biography()`
- Step 4: Scrape driver news with `scrape_driver_news()`

### 2 - RAG

#### 2.1 - Prepare document chunk
