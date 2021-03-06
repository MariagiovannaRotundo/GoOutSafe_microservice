from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    current_app,
)
from src.forms import PhotoGalleryForm, ReviewForm, ReservationForm, DishForm
from src.services import RestaurantServices
from src.auth import roles_allowed
from flask_login import current_user, login_required
from src.forms import RestaurantForm, RestaurantTableForm
from src.utils.formatter import my_date_formatter_iso
from src.services.user_service import UserService
from src.model.dish_model import DishModel
from src.model.table_model import TableModel
from src.model.photo_model import PhotoModel

restaurants = Blueprint("restaurants", __name__)

_max_seats = 6

@restaurants.route("/restaurant/<restaurant_id>")
def restaurant_sheet(restaurant_id):
    weekDaysLabel = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    model = RestaurantServices.get_all_restaurants_info(restaurant_id)
    if model is None:
        render_template(
            "generic_error.html",
            "An error occurred processing your request. Please try again later.",
        )

    review_form = ReviewForm()
    book_form = ReservationForm()

    return render_template(
        "restaurantsheet.html",
        weekDaysLabel=weekDaysLabel,
        id=restaurant_id,
        name=model.name,
        lat=model.lat,
        lon=model.lon,
        phone=model.phone,
        covid_measures=model.covid_measures,
        hours=model.opening_hours,
        cuisine=model.cusine,
        photos=model.photos,
        dishes=model.dishes,
        review_form=review_form,
        book_form=book_form,
        reviews=RestaurantServices.get_three_reviews(restaurant_id),
        _test="visit_rest_test",
    )


@restaurants.route("/restaurant/create", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def create_restaurant():
    """
    This flask method give the possibility with a POST request to create a new
    restaurant inside the system
    """
    form = RestaurantForm()
    if request.method == "POST":
        # TODO check why it's not working this if statement below
        # if form.validate_on_submit():
        current_app.logger.debug(
            "Check if user {} si present".format(current_user.email)
        )
        user = UserService.user_is_present(current_user.email)
        if user is None:
            return render_template(
                "create_restaurant.html",
                _test="anonymus_user_test",
                form=form,
                message="User not logged",
            )

        # create the restaurant
        newrestaurant = RestaurantServices.create_new_restaurant(
            form, current_user.id, _max_seats
        )
        if newrestaurant is None:
            return render_template(
                "create_restaurant.html",
                _test="create_rest_failed",
                form=form,
                message="Error on create services",
            )
        session["RESTAURANT_ID"] = newrestaurant.id
        session["RESTAURANT_NAME"] = newrestaurant.name
        return redirect("/")
    return render_template(
        "create_restaurant.html", _test="create_rest_test", form=form
    )


@restaurants.route("/restaurant/reservations")
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_reservations():
    # http://localhost:5000/my_reservations?fromDate=2013-10-07&toDate=2014-10-07&email=john.doe@email.com

    # for security reason, that are retrive on server side, not passed by params
    owner_id = current_user.id
    restaurant_id = session["RESTAURANT_ID"]

    # filter params
    fromDate = request.args.get("fromDate", type=str)
    toDate = request.args.get("toDate", type=str)
    email = request.args.get("email", type=str)

    reservations_as_list = RestaurantServices.get_reservation_rest(
        restaurant_id, fromDate, toDate
    )
    if reservations_as_list is None:
        reservations_as_list = []

    return render_template(
        "reservations.html",
        _test="restaurant_reservations_test",
        reservations_as_list=reservations_as_list,
        my_date_formatter_iso=my_date_formatter_iso,
        reservations_n=RestaurantServices.get_restaurant_people(restaurant_id),
    )


@restaurants.route("/restaurant/data", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_data():
    """
    This API call give the possibility to the user modify the restaurants
    """
    message = None
    if request.method == "POST":
        # update restaurant
        restaurant_modified = RestaurantServices.update_restaurant(
            session["RESTAURANT_ID"],
            request.form.get("name"),
            request.form.get("lat"),
            request.form.get("lon"),
            request.form.get("covid_measures"),
        )
        # if no resturant match the update query (session problem probably)
        if restaurant_modified:
            message = "Some errors occurs during modification. PLease try again later"
        else:
            message = "Restaurant data has been modified."

    # get the restaurants info and fill the form
    # this part is both for POST and GET requests
    restaurant = RestaurantServices.get_rest_by_id(session["RESTAURANT_ID"])
    if restaurant is not None:
        form = RestaurantForm(obj=restaurant)
        form2 = RestaurantTableForm()
        # get all tables
        tables = RestaurantServices.get_restaurant_tables(session["RESTAURANT_ID"])
        return render_template(
            "restaurant_data.html",
            form=form,
            only=["name", "lat", "lon", "covid_measures"],
            tables=tables,
            form2=form2,
            message=message,
        )
    else:
        return redirect("/restaurant/create")


@restaurants.route("/restaurant/tables", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_tables():
    if request.method == "POST":
        # insert the table with data provided by the form
        table = TableModel()
        table.restaurant_id = session["RESTAURANT_ID"]
        table.max_seats = int(request.form.get("capacity"))
        table.name = request.form.get("name")
        if RestaurantServices.add_table(table) is None:
            return render_template(
                "generic_error.html",
                "An error occured while inserting the table. Please try again later.",
            )
        ##
        return redirect("/restaurant/data")

    elif request.method == "GET":
        # delete the table specified by the get request
        if RestaurantServices.delete_table(request.args.get("id")) is None:
            return render_template(
                "generic_error.html",
                "An error occured while deleting the table. Please try again later.",
            )

        return redirect("/restaurant/data")


@restaurants.route("/restaurant/menu", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_menu():
    if "RESTAURANT_ID" in session:
        # get all dishes
        # dishes = MenuDish.query.filter_by(restaurant_id=session["RESTAURANT_ID"]).all()
        dishes = RestaurantServices.get_dishes_restaurant(session["RESTAURANT_ID"])
        if dishes is None:
            return render_template(
                "generic_error.html",
                message="An error occured accessing data. Please try again later.",
            )
    else:
        dishes = []
    _test = "menu_view_test"
    if request.method == "POST":
        form = DishForm()
        # add dish to the db
        if form.validate_on_submit():
            dish = DishModel()
            dish.name = form.data["name"]
            dish.price = form.data["price"]
            dish.restaurant_id = session["RESTAURANT_ID"]
            result = RestaurantServices.insert_dish(dish)
            if result is None:
                return render_template(
                    "restaurant_menu.html",
                    _test=_test,
                    form=form,
                    dishes=dishes,
                    error="An error occurs inserting you dish. Please try again later.",
                )
            else:
                return redirect("/restaurant/menu")

        else:
            _test = "menu_ko_form_test"
            print(form.errors)
            return render_template(
                "restaurant_menu.html",
                _test=_test,
                form=form,
                dishes=dishes,
                error=form.errors,
            )
    form = DishForm()
    return render_template(
        "restaurant_menu.html",
        _test=_test,
        form=form,
        dishes=dishes,
    )


@restaurants.route("/restaurant/menu/delete/<dish_id>")
@login_required
@roles_allowed(roles=["OPERATOR"])
def delete_dish(dish_id):
    result = RestaurantServices.delete_dish(dish_id)
    if result is None:
        return render_template(
            "generic_error.html",
            message="An error occured deleting your dish. Please try again later.",
        )
    return redirect("/restaurant/menu")


@restaurants.route("/restaurant/photogallery", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_photogallery():
    if request.method == "POST":
        form = PhotoGalleryForm()
        # add photo to the db
        if form.validate_on_submit():
            photo = PhotoModel()
            photo.caption = form.data["caption"]
            photo.url = form.data["url"]
            photo.restaurant_id = session["RESTAURANT_ID"]
            photo = RestaurantServices.add_photo(photo)
            if photo is None:
                return render_template(
                    "generic_error.html",
                    message="An error occured inserting your photo. PLease try again later.",
                )

        return redirect("/restaurant/photogallery")
    else:
        # get all photos
        photos = RestaurantServices.get_photos_restaurants(session["RESTAURANT_ID"])
        if photos is None:
            return render_template(
                "generic_error.html",
                "An error occurred getting all photos. Please try again later.",
            )
        form = PhotoGalleryForm()
        return render_template("photogallery.html", form=form, photos=photos)


@restaurants.route("/restaurant/review/<restaurant_id>", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["CUSTOMER"])
def restaurant_review(restaurant_id):
    if request.method == "POST":
        form = ReviewForm()
        review = RestaurantServices.review_restaurant(
            restaurant_id, current_user.email, form.data["stars"], form.data["review"]
        )
        if review is not None:
            current_app.logger.debug("Review inserted!")
            return render_template(
                "review.html",
                _test="review_done_test",
                restaurant_name=RestaurantServices.get_restaurant_name(restaurant_id),
                review=review,
            )
        # TODO create a call to refresh the ration of this restautats
        # DispatcherMessage.send_message(CALCULATE_RATING_RESTAURANT, [restaurant_id])
        current_app.logger.debug("New rating event ran")
    return render_template(
        "review.html",
        _test="review_done_test",
        error="An error occur inserting the review. Try again later.",
    )


@restaurants.route("/restaurant/search/<name_rest>", methods=["GET"])
def search_restaurant(name_rest):
    current_app.logger.debug(
        "An user want search a restaurant with name {}".format(name_rest)
    )

    file = "index.html"
    if "ROLE" in session and session["ROLE"] == "CUSTOMER":
        file = "index_customer.html"

    form = ReservationForm()
    filter_by_name = RestaurantServices.get_restaurants_by_keyword(name=name_rest)
    return render_template(
        file,
        _test="rest_search_test",
        restaurants=filter_by_name,
        search=name_rest,
        form=form,
    )


@restaurants.route("/restaurant/checkinreservations/<reservation_id>")
@login_required
@roles_allowed(roles=["OPERATOR"])
def checkin_reservations(reservation_id):
    RestaurantServices.checkin_reservations(reservation_id)
    return redirect("/restaurant/reservations")
