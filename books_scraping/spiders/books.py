from typing import Any

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.rating_dict = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

    def parse(self, response: Response, **kwargs) -> Any:
        for book in response.css("article.product_pod"):
            book_detailed_page = response.urljoin(
                book.css("h3 a::attr(href)").get()
            )
            yield response.follow(
                book_detailed_page, callback=self.parse_book_detail
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_detail(self, response: Response) -> Any:
        detail_book_info = {}

        for i, property_name in enumerate(
            response.css("table.table tr th::text").getall()
        ):
            detail_book_info[property_name] = response.css(
                "table.table tr td::text"
            ).getall()[i]

        yield {
            "title": response.css("div h1::text").get(),
            "price": float(detail_book_info.get("Price (incl. tax)")[1:]),
            "amount_in_stock": int(
                detail_book_info.get("Availability")
                .split()[2]
                .replace("(", "")
            ),
            "rating": self.rating_dict[
                response.css("p.star-rating::attr(class)").get().split()[-1]
            ],
            "category": response.css("ul.breadcrumb li a::text").getall()[-1],
            "description": response.css("article.product_page p::text").get(),
            "upc": detail_book_info.get("UPC"),
        }
