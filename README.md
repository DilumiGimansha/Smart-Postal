# Smart-Postal-system 

# manage mail  addresses with priority tagging (Urgent/Regular) and address validation.




## Features

- ✅ Manual address entry with validation
- ✅ CSV bulk upload functionality
- ✅ Priority tagging (Urgent/Regular)
- ✅ Time window scheduling for urgent deliveries
- ✅ Address geocoding using OpenStreetMap
- ✅ RESTful API backend
- ✅ Modern responsive UI

## Technology Stack

### Backend
- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Database**: MySQL 8.x

### Frontend
- **Framework**: React 18.x
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `GET /api/route-addresses/` - List all addresses
- `POST /api/route-addresses/` - Create new address
- `POST /api/route-addresses/bulk_upload/` - Bulk CSV upload
- `GET /api/route-addresses/validate_address/` - Validate address


## sample Endpoints[Optional]

- `GET /api/delivery-addresses/` - List all addresses
- `POST /api/delivery-addresses/` - Create new address
- `POST /api/delivery-addresses/bulk_upload/` - Bulk CSV upload
- `GET /api/delivery-addresses/validate_address/` - Validate address
## Development Status

- [x] Initial project setup
- [x] Database models and migrations
- [x] REST API endpoints
- [x] Frontend UI components
- [ ] Route optimization algorithm
- [ ] Real-time tracking