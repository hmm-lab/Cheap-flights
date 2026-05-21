# Cheap Flights Finder

A web app that searches the **Amadeus API** for the cheapest available flights.

## Features

- Search one-way or round-trip flights
- Live airport/city autocomplete
- Flexible date picker
- Passengers: adults + children
- Results sorted by price (cheapest first)
- Shows stops, duration, flight number, seats remaining

## Setup

### 1. Get free Amadeus API credentials

1. Sign up at [developers.amadeus.com](https://developers.amadeus.com)
2. Create a new app — you get a **Client ID** and **Client Secret** (test environment)

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your credentials
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Notes

- The free Amadeus test environment uses sample data — real fares appear in production mode
- To switch to production, set `hostname='production'` in the `Client()` call in `app.py`
