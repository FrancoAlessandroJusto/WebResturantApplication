Web application for a restaurant ordering and management system with THREE DISTINCT MODES.
The application must clearly separate logic and interface between modes.
The menu is NOT static. The menu is created and modified only in Management Mode.
Other modes must load the menu dynamically through backend API calls.

The interface must be designed for restaurant environments: fast interaction, large clickable elements, minimal cognitive load.

APPLICATION STRUCTURE

The application contains three main modes accessible from a top navigation bar:

Management

Order Taking

Analytics

Each mode must have its own layout and purpose.

GLOBAL UI LAYOUT

The interface must use a modern dashboard layout with:

top navigation bar with application title and mode selector

left sidebar for navigation inside the current mode

main content area

optional right panel for contextual information

Design requirements:

clean professional dashboard style

light background

accent color (orange or warm tone)

rounded cards

clear spacing and visual hierarchy

modern sans-serif typography

optimized for desktop and tablet screens

MODE 1 — MANAGEMENT MODE

Purpose: create and manage the pizza menu.

Target user: restaurant manager with no technical skills.

Layout:

Left sidebar navigation:

Pizzas

Ingredients

Staff

Stock

Main content area divided into two panels.

LEFT PANEL: Create New Pizza

Form fields:

Pizza Name

Sale Price

Production Cost

Ingredients section:

Table-like input with rows containing:

Ingredient name

Weight in grams

remove row button

Button to add new ingredient row.

Primary action button:

Save New Pizza

RIGHT PANEL: Menu Items

Scrollable list of existing pizzas displayed as cards.

Each card must show:

Pizza name

Sale price

production cost

edit button

delete button

UX requirements:

extremely simple layout

large input fields

clear labels

success or error feedback messages

tablet friendly

MODE 2 — ORDER TAKING MODE

Purpose: allow waiters to quickly create customer orders.

Layout with three columns.

LEFT COLUMN: categories navigation

pizzas

drinks

sides

desserts

CENTER COLUMN: pizza menu grid

Menu items displayed as cards.

Each card contains:

pizza image

pizza name

short description

price

quantity selector with + and - buttons

Grid layout responsive with multiple cards per row.

RIGHT COLUMN: current order panel

Contains:

table number input

guest count input

list of ordered items

item quantity

edit options (example: remove ingredient)

order notes

Order summary section:

subtotal

tax

total

Primary action button:

Confirm Order

UX requirements:

extremely fast interaction

touch-friendly controls

minimal text

optimized for tablets used by waiters

MODE 3 — ANALYTICS MODE

Purpose: provide simple business insights for the restaurant owner.

Layout:

Left sidebar with sections:

Overview

Sales report

Menu performance

Customer insights

Settings

Main dashboard area with metric cards.

Top row cards:

Total Revenue

Production Cost

Net Profit

Each card shows:

numeric value

small percentage trend indicator

Below the cards:

Table showing performance per pizza.

Columns:

pizza name

quantity sold

total revenue

production cost

net profit

performance indicator

Add simple filters:

daily

weekly

monthly

UX requirements:

very clear information hierarchy

easy to read numbers

simple charts or tables

understandable at a glance

no accounting terminology

TECHNICAL CONSTRAINTS

Frontend:

HTML
CSS
JavaScript

Backend interaction via REST API.

Example endpoints:

GET /menu
POST /orders
GET /analytics
POST /mgmt/pizze

Authentication is not required.

The UI must clearly separate the three modes in both navigation and layout.

DESIGN STYLE

Professional restaurant dashboard

Minimal design

High usability

Large clickable elements

Soft shadows and rounded cards

Consistent color system

Focus on speed and clarity