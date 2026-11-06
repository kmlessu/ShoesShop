SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';
SET default_table_access_method = heap;

CREATE TABLE public.order_items (
    order_item_id integer NOT NULL,
    order_id integer NOT NULL,
    product_id character varying(50) NOT NULL,
    quantity integer NOT NULL,
    CONSTRAINT order_items_quantity_check CHECK ((quantity > 0))
);
ALTER TABLE public.order_items OWNER TO postgres;

CREATE SEQUENCE public.order_items_order_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.order_items_order_item_id_seq OWNER TO postgres;

ALTER SEQUENCE public.order_items_order_item_id_seq OWNED BY public.order_items.order_item_id;

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    order_date date NOT NULL,
    delivery_date date NOT NULL,
    warehouse_id integer NOT NULL,
    customer_id integer NOT NULL,
    pickup_code character varying(20) NOT NULL,
    status character varying(50) NOT NULL
);
ALTER TABLE public.orders OWNER TO postgres;

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.orders_order_id_seq OWNER TO postgres;

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;

CREATE TABLE public.products (
    sku character varying(50) NOT NULL,
    name character varying(300) NOT NULL,
    unit character varying(50),
    price integer NOT NULL,
    description text,
    supplier character varying(100),
    manufacturer character varying(100),
    photo_filename character varying(255),
    discount integer DEFAULT 0,
    category character varying(50),
    quantity integer DEFAULT 0 NOT NULL,
    CONSTRAINT products_discount_check CHECK ((discount >= 0)),
    CONSTRAINT products_quantity_check CHECK ((quantity >= 0))
);
ALTER TABLE public.products OWNER TO postgres;

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.products_product_id_seq OWNER TO postgres;

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.sku;

CREATE TABLE public.roles (
    role_id integer NOT NULL,
    role_name character varying(50) NOT NULL
);
ALTER TABLE public.roles OWNER TO postgres;

CREATE SEQUENCE public.roles_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.roles_role_id_seq OWNER TO postgres;

ALTER SEQUENCE public.roles_role_id_seq OWNED BY public.roles.role_id;

CREATE TABLE public.stock_levels (
    stock_id integer NOT NULL,
    product_id character varying(50) NOT NULL,
    warehouse_id integer NOT NULL,
    quantity integer DEFAULT 0 NOT NULL
);
ALTER TABLE public.stock_levels OWNER TO postgres;

CREATE SEQUENCE public.stock_levels_stock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.stock_levels_stock_id_seq OWNER TO postgres;

ALTER SEQUENCE public.stock_levels_stock_id_seq OWNED BY public.stock_levels.stock_id;

CREATE TABLE public.users (
    user_id integer NOT NULL,
    login character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(200),
    role_id integer NOT NULL
);
ALTER TABLE public.users OWNER TO postgres;

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;

CREATE TABLE public.warehouses (
    warehouse_id integer NOT NULL,
    address text
);
ALTER TABLE public.warehouses OWNER TO postgres;

CREATE SEQUENCE public.warehouses_warehouse_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.warehouses_warehouse_id_seq OWNER TO postgres;

ALTER SEQUENCE public.warehouses_warehouse_id_seq OWNED BY public.warehouses.warehouse_id;

ALTER TABLE ONLY public.order_items ALTER COLUMN order_item_id SET DEFAULT nextval('public.order_items_order_item_id_seq'::regclass);
ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);
ALTER TABLE ONLY public.products ALTER COLUMN sku SET DEFAULT nextval('public.products_product_id_seq'::regclass);
ALTER TABLE ONLY public.roles ALTER COLUMN role_id SET DEFAULT nextval('public.roles_role_id_seq'::regclass);
ALTER TABLE ONLY public.stock_levels ALTER COLUMN stock_id SET DEFAULT nextval('public.stock_levels_stock_id_seq'::regclass);
ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);
ALTER TABLE ONLY public.warehouses ALTER COLUMN warehouse_id SET DEFAULT nextval('public.warehouses_warehouse_id_seq'::regclass);

COPY public.order_items (order_item_id, order_id, product_id, quantity) FROM stdin;
1	1	А112Т4	2
2	1	F635R4	2
3	2	H782T5	1
4	2	G783F5	1
5	3	J384T6	10
6	3	D572U8	10
7	4	F572H7	5
8	4	D329H3	4
9	5	А112Т4	2
10	5	F635R4	2
11	6	H782T5	1
12	6	G783F5	1
13	7	J384T6	10
14	7	D572U8	10
15	8	F572H7	5
16	8	D329H3	4
17	9	B320R5	5
18	9	G432E4	1
19	10	S213E3	5
20	10	E482R4	5
\.

COPY public.orders (order_id, order_date, delivery_date, warehouse_id, customer_id, pickup_code, status) FROM stdin;
1	2025-02-27	2025-04-20	1	1	901	Завершен
2	2022-09-28	2025-04-21	11	4	902	Завершен
3	2025-03-21	2025-04-22	2	5	903	Завершен
4	2025-02-20	2025-04-23	11	6	904	Завершен
5	2025-03-17	2025-04-24	2	1	905	Завершен
6	2025-03-01	2025-04-25	15	4	906	Завершен
7	2025-02-28	2025-04-26	3	5	907	Завершен
8	2025-03-31	2025-04-27	19	6	908	Новый
9	2025-04-02	2025-04-28	5	1	909	Новый
10	2025-04-03	2025-04-29	19	1	910	Новый
\.

COPY public.products (sku, name, unit, price, description, supplier, manufacturer, photo_filename, discount, category, quantity) FROM stdin;
А112Т4	Ботинки	шт.	4900	Женские Ботинки демисезонные kari	Kari	Kari	1.jpg	3	Женская обувь	5
F635R4	Ботинки	шт.	3244	Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый	Обувь для вас	Marco Tozzi	2.jpg	2	Женская обувь	13
H782T5	Туфли	шт.	4499	Туфли kari мужские классика MYZ21AW-450A, размер 43, цвет: черный	Kari	Kari	3.jpg	4	Мужская обувь	6
G783F5	Ботинки	шт.	5900	Мужские ботинки Рос-Обувь кожаные с натуральным мехом	Kari	Рос	4.jpg	2	Мужская обувь	8
J384T6	Ботинки	шт.	3800	B3430/14 Полуботинки мужские Rieker	Обувь для вас	Rieker	5.jpg	2	Мужская обувь	16
D572U8	Кроссовки	шт.	4100	129615-4 Кроссовки мужские	Обувь для вас	Рос	6.jpg	3	Мужская обувь	14
F572H7	Туфли	шт.	2700	Туфли Marco Tozzi женские летние, размер 39, цвет черный	Kari	Marco Tozzi	7.jpg	2	Женская обувь	12
D329H3	Полуботинки	шт.	1890	Полуботинки Alessio Nesca женские 3-30797-47, размер 37, цвет: бордовый	Обувь для вас	Alessio Nesca	8.jpg	4	Женская обувь	4
B320R5	Туфли	шт.	4300	Туфли Rieker женские демисезонные, размер 41, цвет коричневый	Kari	Rieker	9.jpg	2	Женская обувь	15
G432E4	Туфли	шт.	2800	Туфли kari женские TR-YR-413017, размер 37, цвет: черный	Kari	Kari	10.jpg	3	Женская обувь	5
S213E3	Полуботинки	шт.	2156	407700/01-01 Полуботинки мужские CROSBY	Обувь для вас	CROSBY	11.jpg	3	Мужская обувь	6
E482R4	Полуботинки	шт.	1800	Полуботинки kari женские MYZ20S-149, размер 41, цвет: черный	Kari	Kari	12.jpg	2	Женская обувь	6
S634B5	Кеды	шт.	5500	Кеды Caprice мужские демисезонные, размер 42, цвет черный	Обувь для вас	CROSBY	13.jpg	3	Мужская обувь	5
K345R4	Полуботинки	шт.	2100	407700/01-02 Полуботинки мужские CROSBY	Обувь для вас	CROSBY	14.jpg	2	Мужская обувь	5
O754F4	Туфли	шт.	5400	Туфли женские демисезонные Rieker артикул 55073-68/37	Обувь для вас	Rieker	15.jpg	4	Женская обувь	6
G531F4	Ботинки	шт.	6600	Ботинки женские зимние ROMER арт. 893167-01 Черный	Kari	Kari	16.jpg	12	Женская обувь	8
J542F5	Тапочки	шт.	500	Тапочки мужские Арт.70701-55-67син р.41	Kari	Kari	17.jpg	13	Мужская обувь	20
B431R5	Ботинки	шт.	2700	Мужские кожаные ботинки/мужские ботинки	Обувь для вас	Rieker	18.jpg	2	Мужская обувь	15
P764G4	Туфли	шт.	6800	Туфли женские, ARGO, размер 38	Kari	CROSBY	19.jpg	15	Женская обувь	5
C436G5	Ботинки	шт.	10200	Ботинки женские, ARGO, размер 40	Kari	Alessio Nesca	20.jpg	15	Женская обувь	5
F427R5	Ботинки	шт.	11800	Ботинки на молнии с декоративной пряжкой FRAU	Обувь для вас	Rieker	21.jpg	15	Женская обувь	5
N457T5	Полуботинки	шт.	4600	Полуботинки Ботинки черные зимние, мех	Kari	CROSBY	22.jpg	3	Женская обувь	5
D364R4	Туфли	шт.	12400	Туфли Luiza Belly женские Kate-lazo черные из натуральной замши	Kari	Kari	23.jpg	16	Женская обувь	5
S326R5	Тапочки	шт.	9900	Мужские кожаные тапочки "Профиль С.Дали"	Обувь для вас	CROSBY	24.jpg	17	Мужская обувь	5
L754R4	Полуботинки	шт.	1700	Полуботинки kari женские WB2020SS-26, размер 38, цвет: черный	Kari	Kari	25.jpg	2	Женская обувь	5
M542T5	Кроссовки	шт.	2800	Кроссовки мужские TOFA	Обувь для вас	Rieker	26.jpg	18	Мужская обувь	5
D268G5	Туфли	шт.	4399	Туфли Rieker женские демисезонные, размер 36, цвет коричневый	Обувь для вас	Rieker	27.jpg	3	Женская обувь	5
T324F5	Сапоги	шт.	4699	Сапоги замша Цвет: синий	Kari	CROSBY	28.jpg	2	Женская обувь	5
K358H6	Тапочки	шт.	599	Тапочки мужские син р.41	Kari	Rieker	29.jpg	20	Мужская обувь	5
H535R5	Ботинки	шт.	2300	Женские Ботинки демисезонные	Обувь для вас	Rieker	30.jpg	2	Женская обувь	5
\.

COPY public.roles (role_id, role_name) FROM stdin;
1	Гость
2	Авторизованный клиент
3	Менеджер
4	Администратор
\.

COPY public.stock_levels (stock_id, product_id, warehouse_id, quantity) FROM stdin;
\.

COPY public.users (user_id, login, password_hash, full_name, role_id) FROM stdin;
1	ldiph5e@tutanota.com	BntwUp	Степанов Михаил Артёмович	3
2	tjde7c@yahoo.com	YOyhfR	Ворсин Петр Евгеньевич	3
3	wpmrc3do@tutanota.com	RSbvHv	Старикова Елена Павловна	3
4	94d5ous@gmail.com	uzWC67	Никифорова Весения Николаевна	4
5	uth4iz@mail.com	2L6KZG	Сазонов Руслан Германович	4
6	yzls62@outlook.com	JIFRCZ	Одинцов Серафим Артёмович	4
7	5d42bu@tutanota.com	rwVDh9	Михайлюк Анна Вячеславовна	2
8	ptec8ym@yahoo.com	LdNyos	Ситдикова Елена Анатольевна	2
9	1qz4kw@mail.com	gynQMT	Ворсин Петр Евгеньевич	2
10	4np65e@mail.com	AtnDjr	Старикова Елена Павловна	2
\.

COPY public.warehouses (warehouse_id, address) FROM stdin;
1	420151, г. Лесной, ул. Вишневая, 32
2	125061, г. Лесной, ул. Подгорная, 8
3	630370, г. Лесной, ул. Шоссейная, 24
4	400562, г. Лесной, ул. Зеленая, 32
5	614510, г. Лесной, ул. Маяковского, 47
6	410542, г. Лесной, ул. Светлая, 46
7	620839, г. Лесной, ул. Цветочная, 8
8	443890, г. Лесной, ул. Коммунистическая, 1
9	603379, г. Лесной, ул. Спортивная, 46
10	603721, г. Лесной, ул. Гоголя, 41
11	410172, г. Лесной, ул. Северная, 13
12	614611, г. Лесной, ул. Молодежная, 50
13	454311, г. Лесной, ул. Новая, 19
14	660007, г. Лесной, ул. Октябрьская, 19
15	603036, г. Лесной, ул. Садовая, 4
16	394060, г. Лесной, ул. Фрунзе, 43
17	410661, г. Лесной, ул. Школьная, 50
18	625590, г. Лесной, ул. Коммунистическая, 20
19	625683, г. Лесной, ул. 8 Марта
20	450983, г. Лесной, ул. Комсомольская, 26
21	394782, г. Лесной, ул. Чехова, 3
22	603002, г. Лесной, ул. Дзержинского, 28
23	450558, г. Лесной, ул. Набережная, 30
24	344288, г. Лесной, ул. Чехова, 1
25	614164, г. Лесной, ул. Степная, 30
26	394242, г. Лесной, ул. Коммунистическая, 43
27	660540, г. Лесной, ул. Солнечная, 25
28	125837, г. Лесной, ул. Шоссейная, 40
29	125703, г. Лесной, ул. Партизанская, 49
30	625283, г. Лесной, ул. Победы, 46
31	614753, г. Лесной, ул. Полевая, 35
32	426030, г. Лесной, ул. Маяковского, 44
33	450375, г. Лесной, ул. Клубная, 44
34	625560, г. Лесной, ул. Некрасова, 12
35	630201, г. Лесной, ул. Комсомольская, 17
36	190949, г. Лесной, ул. Мичурина, 26
\.

SELECT pg_catalog.setval('public.order_items_order_item_id_seq', 20, true);
SELECT pg_catalog.setval('public.orders_order_id_seq', 10, true);
SELECT pg_catalog.setval('public.products_product_id_seq', 1, false);
SELECT pg_catalog.setval('public.roles_role_id_seq', 4, true);
SELECT pg_catalog.setval('public.stock_levels_stock_id_seq', 1, false);
SELECT pg_catalog.setval('public.users_user_id_seq', 10, true);
SELECT pg_catalog.setval('public.warehouses_warehouse_id_seq', 36, true);

ALTER TABLE ONLY public.order_items ADD CONSTRAINT order_items_pkey PRIMARY KEY (order_item_id);
ALTER TABLE ONLY public.orders ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);
ALTER TABLE ONLY public.products ADD CONSTRAINT products_pkey PRIMARY KEY (sku);
ALTER TABLE ONLY public.roles ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);
ALTER TABLE ONLY public.roles ADD CONSTRAINT roles_role_name_key UNIQUE (role_name);
ALTER TABLE ONLY public.stock_levels ADD CONSTRAINT stock_levels_pkey PRIMARY KEY (stock_id);
ALTER TABLE ONLY public.stock_levels ADD CONSTRAINT stock_levels_product_id_warehouse_id_key UNIQUE (product_id, warehouse_id);
ALTER TABLE ONLY public.users ADD CONSTRAINT users_login_key UNIQUE (login);
ALTER TABLE ONLY public.users ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
ALTER TABLE ONLY public.warehouses ADD CONSTRAINT warehouses_pkey PRIMARY KEY (warehouse_id);

CREATE INDEX idx_products_name ON public.products USING btree (name);
CREATE INDEX idx_stock_product ON public.stock_levels USING btree (product_id);

ALTER TABLE ONLY public.order_items ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;
ALTER TABLE ONLY public.order_items ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(sku);
ALTER TABLE ONLY public.orders ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.users(user_id);
ALTER TABLE ONLY public.orders ADD CONSTRAINT orders_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(warehouse_id);
ALTER TABLE ONLY public.stock_levels ADD CONSTRAINT stock_levels_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(sku);
ALTER TABLE ONLY public.stock_levels ADD CONSTRAINT stock_levels_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(warehouse_id) ON DELETE CASCADE;
ALTER TABLE ONLY public.users ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(role_id);