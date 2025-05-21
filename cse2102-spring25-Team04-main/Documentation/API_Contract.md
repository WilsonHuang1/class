# Pet Adoption API Contract

---

## Pet Endpoints

### GET `/pets`
- **Description**: Get all pets (optionally filtered).
- **Input**: None or query parameters (e.g., breed, age, etc.)
- **Output**: JSON array of pet objects.

### GET `/pets/<pet_id>`
- **Description**: Get a pet by ID.
- **Input**: `pet_id` (string)
- **Output**: JSON pet object.

### GET `/pets/featured`
- **Description**: Get featured pets.
- **Input**: None
- **Output**: JSON array of featured pets.

### GET `/pets/nearby`
- **Description**: Get nearby pets.
- **Input**: Query params (e.g. `location`, `radius`)
- **Output**: JSON array of nearby pets.

### POST `/pets`
- **Description**: Add a new pet.
- **Input**: JSON with pet data.
- **Output**: Success/failure message.

### PUT `/pets/<pet_id>`
- **Description**: Update a pet.
- **Input**: `pet_id`, JSON with updated fields.
- **Output**: Updated pet object or message.

### DELETE `/pets/<pet_id>`
- **Description**: Delete a pet.
- **Input**: `pet_id`
- **Output**: Success/failure message.

---

## User Endpoints

### POST `/users/register`
- **Description**: Register new user.
- **Input**: JSON with user details.
- **Output**: Confirmation or error.

### POST `/users/login`
- **Description**: Log in a user.
- **Input**: JSON with email and password.
- **Output**: Auth token or error.

### GET `/users/<user_id>`
- **Description**: Get user profile.
- **Input**: `user_id`
- **Output**: JSON user profile.

### PUT `/users/<user_id>`
- **Description**: Update user profile.
- **Input**: `user_id`, JSON with updates.
- **Output**: Success message.

### GET `/users/<user_id>/favorites`
- **Description**: Get favorite pets.
- **Input**: `user_id`
- **Output**: List of favorite pet IDs or objects.

### POST `/users/<user_id>/favorites/<pet_id>`
- **Description**: Add a pet to favorites.
- **Input**: `user_id`, `pet_id`
- **Output**: Confirmation message.

### DELETE `/users/<user_id>/favorites/<pet_id>`
- **Description**: Remove pet from favorites.
- **Input**: `user_id`, `pet_id`
- **Output**: Confirmation message.

### GET `/users/<user_id>/preferences`
- **Description**: Get user preferences.
- **Input**: `user_id`
- **Output**: JSON with preferences.

### PUT `/users/<user_id>/preferences`
- **Description**: Update user preferences.
- **Input**: `user_id`, JSON
- **Output**: Success message.

---

## Application Endpoints

### POST `/applications`
- **Description**: Submit new application.
- **Input**: JSON application data.
- **Output**: Confirmation or error.

### GET `/applications/<application_id>`
- **Description**: Get application details.
- **Input**: `application_id`
- **Output**: JSON application object.

### GET `/applications/user/<user_id>`
- **Description**: Get user's applications.
- **Input**: `user_id`
- **Output**: List of applications.

### PUT `/applications/<application_id>`
- **Description**: Update application.
- **Input**: `application_id`, JSON
- **Output**: Success or error.

### PUT `/applications/<application_id>/status`
- **Description**: Update application status.
- **Input**: `application_id`, new status in JSON.
- **Output**: Success or error.

---

## Appointment Endpoints

### POST `/appointments`
- **Description**: Schedule appointment.
- **Input**: JSON with appointment info.
- **Output**: Confirmation.

### GET `/appointments/<appointment_id>`
- **Description**: Get appointment info.
- **Input**: `appointment_id`
- **Output**: JSON appointment object.

### GET `/appointments/user/<user_id>`
- **Description**: Get user appointments.
- **Input**: `user_id`
- **Output**: List of appointments.

### PUT `/appointments/<appointment_id>`
- **Description**: Update appointment.
- **Input**: `appointment_id`, JSON
- **Output**: Updated info.

### DELETE `/appointments/<appointment_id>`
- **Description**: Cancel appointment.
- **Input**: `appointment_id`
- **Output**: Confirmation.

---

## Contact Endpoint

### POST `/contact`
- **Description**: Contact the shelter.
- **Input**: JSON with name, email, and message.
- **Output**: Confirmation message.

---

## Tips Endpoints

### GET `/tips`
- **Description**: Get adoption tips.
- **Input**: None
- **Output**: List of tips.

### GET `/tips/<tip_id>`
- **Description**: Get specific tip.
- **Input**: `tip_id`
- **Output**: Tip object.

---

## Status

### GET `/`
- **Description**: API root.
- **Input**: None
- **Output**: JSON with welcome/status message.
