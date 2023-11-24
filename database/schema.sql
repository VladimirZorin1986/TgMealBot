-- CREATE CUSTOMER TABLES

CREATE TABLE canteen (
    id_canteen SMALLINT GENERATED ALWAYS AS IDENTITY,
    canteen_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_canteen)
);

CREATE TABLE delivery_place (
    id_delivery_place SMALLINT GENERATED ALWAYS AS IDENTITY,
    place_name VARCHAR(80) NOT NULL,
    id_canteen SMALLINT NOT NULL,
    begin_date DATE NOT NULL,
    end_date DATE,
    custom_menu_flg BOOLEAN,
    PRIMARY KEY (id_delivery_place),
    CONSTRAINT fk_canteen
        FOREIGN KEY (id_canteen)
        REFERENCES canteen (id_canteen)
        ON DELETE CASCADE
);

CREATE TABLE customer (
    id_customer INT GENERATED ALWAYS AS IDENTITY,
    id_eis_sbj INT NOT NULL,
    id_user BIGINT,
    phone_number CHAR(12) NOT NULL,
    id_delivery_place SMALLINT,
    PRIMARY KEY (id_customer),
    CONSTRAINT fk_delivery_place
        FOREIGN KEY (id_delivery_place)
        REFERENCES delivery_place (id_delivery_place)
        ON DELETE SET NULL
);

CREATE TABLE customer_permission (
    id_permission INT GENERATED ALWAYS AS IDENTITY,
    beg_date DATE NOT NULL,
    end_date DATE,
    canteen_id SMALLINT NOT NULL,
    customer_id SMALLINT NOT NULL
    PRIMARY KEY (id_permission),
    CONSTRAINT fk_canteen3
        FOREIGN KEY (canteen_id)
        REFERENCES canteen (id_canteen)
        ON DELETE CASCADE,
    CONSTRAINT fk_customer2
        FOREIGN KEY (customer_id)
        REFERENCES customer (id_customer)
        ON DELETE CASCADE
)

-- CREATE MENU TABLES

CREATE TABLE meal_type (
    id_meal_type SMALLINT GENERATED ALWAYS AS IDENTITY,
    meal_type_name VARCHAR(20) NOT NULL,
    PRIMARY KEY (id_meal_type)
);

CREATE TABLE menu (
    id_menu INT GENERATED ALWAYS AS IDENTITY,
    id_canteen SMALLINT NOT NULL,
    id_meal_type SMALLINT NOT NULL,
    menu_date DATE NOT NULL,
    menu_name VARCHAR(120) NOT NULL,
    beg_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    PRIMARY KEY (id_menu),
    CONSTRAINT fk_canteen2
        FOREIGN KEY (id_canteen)
        REFERENCES canteen (id_canteen)
        ON DELETE CASCADE,
    CONSTRAINT fk_meal_type
        FOREIGN KEY (id_meal_type)
        REFERENCES meal_type (id_meal_type)
        ON DELETE RESTRICT
);

CREATE TABLE menu_position (
    id_menu_pos BIGINT GENERATED ALWAYS AS IDENTITY,
    id_menu INT NOT NULL,
    dish_name VARCHAR(120) NOT NULL,
    weight VARCHAR(40),
    cost MONEY,
    quantity SMALLINT DEFAULT 1,
    PRIMARY KEY (id_menu_pos),
    CONSTRAINT fk_menu
        FOREIGN KEY (id_menu)
        REFERENCES menu (id_menu)
        ON DELETE CASCADE
);

-- CREATE ORDER TABLES

CREATE TABLE meal_order (
    id_order INT GENERATED ALWAYS AS IDENTITY,
    id_customer INT NOT NULL,
    id_menu INT NOT NULL,
    order_date DATE NOT NULL,
    amt MONEY,
    PRIMARY KEY (id_order),
    CONSTRAINT fk_customer
        FOREIGN KEY (id_customer)
        REFERENCES customer (id_customer)
        ON DELETE CASCADE,
    CONSTRAINT fk_menu2
        FOREIGN KEY (id_menu)
        REFERENCES menu (id_menu)
        ON DELETE RESTRICT
);

CREATE TABLE order_detail (
    id_order_detail BIGINT GENERATED ALWAYS AS IDENTITY,
    id_order INT NOT NULL,
    id_menu_pos BIGINT NOT NULL,
    quantity SMALLINT NOT NULL,
    PRIMARY KEY (id_order_detail),
    CONSTRAINT fk_order
        FOREIGN KEY (id_order)
        REFERENCES meal_order (id_order)
        ON DELETE CASCADE,
    CONSTRAINT fk_menu_pos
        FOREIGN KEY (id_menu_pos)
        REFERENCES menu_position (id_menu_pos)
        ON DELETE RESTRICT
);

