-- CREATE CUSTOMER TABLES

CREATE TABLE canteen (
    canteen_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    canteen_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (canteen_id)
);

CREATE TABLE delivery_place (
    place_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    place_name VARCHAR(80) NOT NULL,
    canteen_id SMALLINT NOT NULL,
    begin_date DATE NOT NULL,
    end_date DATE,
    custom_menu_flg BOOLEAN,
    PRIMARY KEY (place_id),
    CONSTRAINT fk_canteen
        FOREIGN KEY (canteen_id)
        REFERENCES canteen (canteen_id)
        ON DELETE CASCADE
);

CREATE TABLE customer (
    customer_id INT GENERATED ALWAYS AS IDENTITY,
    eis_sbj_id INT NOT NULL,
    tg_id BIGINT UNIQUE NULLS NOT DISTINCT,
    phone_number CHAR(12) UNIQUE NOT NULL,
    place_id SMALLINT,
    PRIMARY KEY (customer_id),
    CONSTRAINT fk_delivery_place
        FOREIGN KEY (place_id)
        REFERENCES delivery_place (place_id)
        ON DELETE SET NULL
);

CREATE TABLE customer_permission (
    permission_id INT GENERATED ALWAYS AS IDENTITY,
    beg_date DATE NOT NULL,
    end_date DATE,
    canteen_id SMALLINT NOT NULL,
    customer_id SMALLINT NOT NULL
    PRIMARY KEY (permission_id),
    CONSTRAINT fk_canteen3
        FOREIGN KEY (canteen_id)
        REFERENCES canteen (canteen_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_customer2
        FOREIGN KEY (customer_id)
        REFERENCES customer (customer_id)
        ON DELETE CASCADE
)

-- CREATE MENU TABLES

CREATE TABLE meal_type (
    type_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    type_name VARCHAR(20) NOT NULL,
    PRIMARY KEY (type_id)
);

CREATE TABLE menu (
    menu_id INT GENERATED ALWAYS AS IDENTITY,
    canteen_id SMALLINT NOT NULL,
    type_id SMALLINT NOT NULL,
    menu_date DATE NOT NULL,
    menu_name VARCHAR(120) NOT NULL,
    beg_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    PRIMARY KEY (menu_id),
    CONSTRAINT fk_canteen2
        FOREIGN KEY (canteen_id)
        REFERENCES canteen (canteen_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_meal_type
        FOREIGN KEY (type_id)
        REFERENCES meal_type (type_id)
        ON DELETE RESTRICT
);

CREATE TABLE menu_position (
    menu_pos_id BIGINT GENERATED ALWAYS AS IDENTITY,
    menu_id INT NOT NULL,
    dish_name VARCHAR(120) NOT NULL,
    weight VARCHAR(40),
    cost NUMERIC(10,2),
    quantity SMALLINT DEFAULT 1,
    PRIMARY KEY (menu_pos_id),
    CONSTRAINT fk_menu
        FOREIGN KEY (menu_id)
        REFERENCES menu (menu_id)
        ON DELETE CASCADE
);

-- CREATE ORDER TABLES

CREATE TABLE meal_order (
    order_id INT GENERATED ALWAYS AS IDENTITY,
    customer_id INT NOT NULL,
    menu_id INT NOT NULL,
    order_date DATE NOT NULL,
    amt MONEY,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES customer (customer_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_menu2
        FOREIGN KEY (menu_id)
        REFERENCES menu (menu_id)
        ON DELETE RESTRICT
);

CREATE TABLE order_detail (
    detail_id BIGINT GENERATED ALWAYS AS IDENTITY,
    order_id INT NOT NULL,
    menu_pos_id BIGINT NOT NULL,
    quantity SMALLINT NOT NULL,
    PRIMARY KEY (id_order_detail),
    CONSTRAINT fk_order
        FOREIGN KEY (order_id)
        REFERENCES meal_order (order_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_menu_pos
        FOREIGN KEY (menu_pos_id)
        REFERENCES menu_position (menu_pos_id)
        ON DELETE RESTRICT
);

