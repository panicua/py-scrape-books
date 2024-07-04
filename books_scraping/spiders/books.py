from typing import Any

import scrapy
from scrapy.http import Response

RATING_DICT = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

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
            "title": self.get_title(response),
            "price": self.get_price(detail_book_info),
            "amount_in_stock": self.get_amount_in_stock(detail_book_info),
            "rating": self.get_rating(response),
            "category": self.get_category(response),
            "description": self.get_description(response),
            "upc": self.get_upc(detail_book_info),
        }

    @staticmethod
    def get_title(response: Response) -> str:
        return response.css("div h1::text").get()

    @staticmethod
    def get_price(detail_book_info: dict) -> float:
        return float(detail_book_info.get("Price (incl. tax)")[1:])

    @staticmethod
    def get_amount_in_stock(detail_book_info: dict) -> int:
        return int(
            detail_book_info.get("Availability")
            .split()[2]
            .replace("(", "")
        )

    @staticmethod
    def get_rating(response: Response) -> int:
        return RATING_DICT[
            response.css("p.star-rating::attr(class)").get().split()[-1]
        ]

    @staticmethod
    def get_category(response: Response) -> str:
        return response.css("ul.breadcrumb li a::text").getall()[-1]

    @staticmethod
    def get_description(response: Response) -> str:
        return response.css("div#product_description ~ p::text").get()

    @staticmethod
    def get_upc(detail_book_info: dict) -> str:
        return detail_book_info.get("UPC")
