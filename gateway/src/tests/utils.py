from datetime import time, datetime
from random import randrange

from src.forms import (
    RestaurantForm,
    SearchUserForm,
    ReviewForm,
    DishForm,
    ReservationForm,
    PhotoGalleryForm,
    UserForm,
)
from src.model import UserModel
from src.services import *
from src.services.booking_services import BookingServices
from src.model.review_model import ReviewModel


def login(client, username, password):
    return client.post(
        "/login",
        data=dict(
            email=username,
            password=password,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def logout(client):
    return client.get("/logout", follow_redirects=True)


def register_user(client, user: UserForm, role_id: int = 3):
    """
    This method perform the request to register a new user
    :param client: Is a flask app created inside the fixtures
    :param user: Is the User form populate with the mock data
    :return: response from URL "/user/create_user"
    """
    data = dict(
        email=user.email.data,
        firstname=user.firstname.data,
        lastname=user.lastname.data,
        password=user.password.data,
        dateofbirth=user.dateofbirth.data,
        phone=user.phone.data,
        submit=True,
        headers={"Content-type": "application/x-www-form-urlencoded"},
    )
    if role_id == 2:
        return client.post("/user/create_operator", data=data, follow_redirects=True)
    return client.post("/user/create_user", data=data, follow_redirects=True)


def register_restaurant(client, restaurant: RestaurantForm):
    """
    This method perform the request  to build a new restaurant
    :param client: Is a flask app created inside the fixtures
    :param restaurant: Is the restaurant form populate with the mock data
    :return: response from URL "/create_restaurant"
    """
    return client.post(
        "/restaurant/create",
        data=dict(
            name=restaurant.name.data,
            phone=restaurant.phone.data,
            lat=restaurant.lat.data,
            lon=restaurant.lon.data,
            n_tables=restaurant.n_tables.data,
            covid_measures=restaurant.covid_measures.data,
            cuisine=restaurant.cuisine.data,
            open_days=restaurant.open_days.data,
            open_lunch=restaurant.open_lunch.data,
            close_lunch=restaurant.close_lunch.data,
            open_dinner=restaurant.open_dinner.data,
            close_dinner=restaurant.close_dinner.data,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def mark_people_for_covid19(client, form: SearchUserForm):
    """
    This method perform the request to mark a people as positive
    :return: response from request
    """
    return client.post(
        "/mark_positive",
        data=dict(
            email=form.email.data,
            phone=form.phone.data,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def visit_restaurant(client, restaurant_id):
    """
    This perform the request to visit the restaurant view
    :param client:
    :param restaurant_id:
    :return: response from client
    """
    return client.get("/restaurant/{}".format(restaurant_id), follow_redirects=True)


def visit_photo_gallery(client):
    """
    This perform the request to visit the photo_gallery view
    :param client:
    :param restaurant_id:
    :return: response from client
    """
    return client.get("/restaurant/photogallery", follow_redirects=True)


def visit_reservation(client, from_date, to_date, email):
    """
    This perform the URL to visit the reservatioin of a restaurants
    ----- This is an example of URL --
    http://localhost:5000/list_reservations?fromDate=2013-10-07&toDate=2014-10-07&email=john.doe@email.com
    """
    return client.get(
        "/restaurant/reservations?fromDate={}&toDate={}&email={}".format(
            from_date, to_date, email
        ),
        follow_redirects=True,
    )


def visit_customer_reservation(client, from_date, to_date):
    """
    This perform the URL to visit the reservatioin of a restaurants
    ----- This is an example of URL --
    http://localhost:5000/list_reservations?fromDate=2013-10-07&toDate=2014-10-07&email=john.doe@email.com
    """
    return client.get(
        "/customer/reservations?fromDate={}&toDate={}".format(from_date, to_date),
        follow_redirects=True,
    )


def make_revew(client, restaurant_id: int, form: ReviewForm):
    """
    perform the flask request to make a new url
    """
    return client.post(
        "/restaurant/review/{}".format(restaurant_id),
        data=dict(
            stars=form.stars.data,
            review=form.review.data,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def research_restaurant(client, name):
    """
    This method is an util method to contains the code to perform the
    flask request to research the user by name or substring
    :param client:
    :param name:
    :return:
    """
    return client.get("/restaurant/search/{}".format(name), follow_redirects=True)


def del_reservation_client(client, id: int):
    """
    TODO
    :param client:
    :param id:
    :return:
    """
    return client.get("/customer/deletereservations/{}".format(id))


def get_reservation(client):
    return client.get("/customer/reservations")


def create_new_menu(client, form: DishForm):
    """
    This util have the code to perform the request with flask client
    and make a new mewnu
    :param form:
    :return:
    """
    return client.post(
        "/restaurant/menu",
        data=dict(
            name=form.name,
            price=form.price,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def create_new_user_with_form(client, form: UserForm, type):
    """
    This util have the code to perform the request with flask client
    and make a new user
    :param form:
    :return:
    """
    return client.post(
        "/user/create_" + type,
        data=dict(
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            password="12345678",
            dateofbirth="22/03/1998",
            phone="1235{}".format(randrange(100000)),
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def create_new_restaurant_with_form(client, restaurant: RestaurantForm):
    """
    This util have the code to perform the request with flask client
    and make a new user
    :param form:
    :return:
    """
    return client.post(
        "/restaurant/create",
        data=dict(
            name=restaurant.name,
            phone=restaurant.phone,
            lat=restaurant.lat,
            lon=restaurant.lon,
            n_tables=restaurant.n_tables,
            cuisine=restaurant.cuisine,
            open_days=restaurant.open_days,
            open_lunch=restaurant.open_lunch,
            close_lunch=restaurant.close_lunch,
            open_dinner=restaurant.open_dinner,
            close_dinner=restaurant.close_dinner,
            covid_measures=restaurant.covid_measures,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def get_today_midnight():
    """
    This method will return a datetime of today at midnight
    """
    return datetime.combine(datetime.today(), datetime.min.time())


def get_user_with_email(email):
    """
    This method factorize the code to get an user with a email
    :param email: the email that we want use to query the user
    :return: return the user if exist otherwise None
    """
    return UserService.user_is_present(email=email)


def get_rest_with_name_and_phone(name, phone):
    """
    This method factorize the code to get an restaurant with a name
    :param name: the email that we want use to query the user
    :return: return the user if exist otherwise None
    """
    reservations = BookingServices.get_all_booking()
    for res in reservations:
        if res["name"] == name and res["phone"] == phone:
            return res
    return None


def get_rest_with_name(name):
    """
    This method factorize the code to get an restaurant with a name
    :param name: the email that we want use to query the user
    :return: return the user if exist otherwise None
    """
    return RestaurantServices.get_restaurants_by_keyword(name)[0]


def create_user_on_db(ran: int = randrange(100000), role_id: int = 3, password=None):
    form = UserForm()
    form.firstname.data = "User_{}".format(ran)
    form.lastname.data = "user_{}".format(ran)
    if password is None:
        form.password.data = "Alibaba{}".format(ran)
    else:
        form.password.data = password
    form.phone.data = "1234562344{}".format(ran)
    form.dateofbirth.data = "1985-12-12"
    form.email.data = "user{}@user.edu".format(str(ran))
    created = UserService.create_user(form, role_id)
    if created is False:
        return None
    return UserService.user_is_present(form.email.data, form.phone.data)


def create_restaurants_on_db(
    name: str = "mock_rest{}".format(randrange(1000, 50000)),
    user_id: int = None,
    user_email: str = None,
    tables: int = 50,
):
    form = RestaurantForm()
    form.name.data = name
    form.phone.data = "1234{}".format(randrange(1000, 50000))
    form.lat.data = 183
    form.lon.data = 134
    form.n_tables.data = tables
    form.covid_measures.data = "We can survive{}".format(randrange(1000, 50000))
    form.cuisine.data = ["Italian food"]
    form.open_days.data = ["0", "1", "2", "3", "4", "5", "6"]
    form.open_lunch.data = time(hour=12, minute=00)
    form.close_lunch.data = time(hour=15, minute=00)
    form.open_dinner.data = time(hour=19, minute=00)
    form.close_dinner.data = time(hour=22, minute=00)
    return RestaurantServices.create_new_restaurant(
        form, user_id=user_id, user_email=user_email, max_sit=6
    )


def del_user_on_db(id):
    UserService.delete_user(user_id=id)


def del_restaurant_on_db(id):
    RestaurantServices.delete_restaurant(id)

def del_friends_of_reservation(id):
    """
    q = db.session.query(Friend).filter_by(reservation_id=id).delete()
    db.session.commit()
    """
    pass


def del_booking_services(id: int, user_id: int):
    """
    :param id: reservation is:
    :return:
    """
    BookingServices.delete_book(id, user_id)


def positive_with_user_id(user_id: int = None, marked: bool = True):
    """
    This method is an util function to search inside the positive user
    """
    users = HealthyServices.report_positive()
    for user in users:
        if user.id == user_id and user.is_positive is marked:
            return user
    return None


def unmark_people_for_covid19(client, form: SearchUserForm):
    """
    This method perform the request to mark a people as not positive
    :return: response from request
    """
    return client.post(
        "/unmark_positive",
        data=dict(
            email=form.email.data,
            phone=form.phone.data,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def search_contact_positive_covid19(client, form: SearchUserForm):
    """
    This method search contacts with a covid19 positive person
    """
    return client.post(
        "/search_contacts",
        data=dict(
            email=form.email.data,
            phone=form.phone.data,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def create_new_reservation(client, form: ReservationForm):
    """
    This util have the code to perform the request with flask client
    and make a new reservation
    :param form:
    :return:
    """
    return client.post(
        "/restaurant/book",
        data=dict(
            reservation_date=form.reservation_date,
            people_number=form.people_number,
            restaurant_id=form.restaurant_id,
            friends=form.friends,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def create_new_photo(client, form: PhotoGalleryForm):
    """
    This util have the code to perform the request with flask client
    and add a new photo
    :param form:
    :return:
    """
    return client.post(
        "/restaurant/photogallery",
        data=dict(
            caption=form.caption,
            url=form.url,
            submit=True,
            headers={"Content-type": "application/x-www-form-urlencoded"},
        ),
        follow_redirects=True,
    )


def register_operator(client, user: UserForm):
    """
    This method perform the request to register a new user
    :param client: Is a flask app created inside the fixtures
    :param user: Is the User form populate with the mock data
    :return: response from URL "/user/create_user"
    """
    client.get("/user/create_operator", follow_redirects=True)
    data = dict(
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        password=user.password,
        dateofbirth=user.dateofbirth,
        phone=user.phone,
        submit=True,
        headers={"Content-type": "application/x-www-form-urlencoded"},
    )
    return client.post("/user/create_operator", data=data, follow_redirects=True)


def create_random_booking(num: int, rest_id: int, user: UserModel, date_time, friends):
    """
    Function to make
    :param num:
    :param rest_id:
    :param user:
    :param date_time:
    :param friends:
    :return:
    """
    people_number = len(friends.split(";")) + 1
    reservation = BookingServices.book(
        rest_id, user, date_time, people_number, friends, True
    )
    return reservation


def del_booking(reservation_id, customer_id):
    return BookingServices.delete_book(reservation_id, customer_id)


def create_review_for_restaurants(
    starts: float,
    rest_id: int,
    reviewer_email: str,
    comment: str = "random_coment{}".format(randrange(100000)),
) -> ReviewModel:
    """
    This method contains the code to add a new review inside the db
    for the restaurant with id
    :param starts: Number of starts
    :param comment: a comment for review, by default a random value
    :param rest_id: restaurants id
    :return Review db object
    """
    review = RestaurantServices.review_restaurant(
        restaurant_id=rest_id,
        reviewer_email=reviewer_email,
        stars=starts,
        review=comment,
    )
    return review
