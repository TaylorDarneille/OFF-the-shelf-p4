# Off-The-Shelf
This is our Project 4 repo for GA.
Change

## Tech Stack
Django
PostgresQL


### Pip installations
- requests
- xmljson


## User Stories

## Wireframes/ERD

## Models

### Wishlist Model

| Column Name | Data Type | Notes |
| --------------- | ------------- | ------------------------------ |
| id | Integer | Serial Primary Key, Auto-generated |
| book_id | Integer | Book id from Goodreads Website |
| title | String | Title of the book |
| img_url | String | Image url of the book |
| user_id | Object | ForeignKey reference to User Model |

### Comment Model

| Column Name | Data Type | Notes |
| --------------- | ------------- | ------------------------------ |
| id | Integer | Serial Primary Key, Auto-generated |
| book_id | Integer | Book id from Goodreads Website |
| title | String | Title of the book |
| content | String | Content of the comment |
| user_id | Object | ForeignKey reference to User Model |
