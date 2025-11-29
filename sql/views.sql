CREATE VIEW customer_orders AS
SELECT c.CustomerID, o.OrderID
FROM customers c
JOIN orders o ON c.CustomerID = o.CustomerID;

CREATE VIEW high_value_customers AS
SELECT c.CustomerID, c.Email
FROM customers c
JOIN customer_orders co ON c.CustomerID = co.CustomerID;
