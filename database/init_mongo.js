db = db.getSiblingDB('ecommerce_db');

db.products.drop();
db.createCollection("products", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["name", "price", "category", "stock"],
         properties: {
            name: {
               bsonType: "string",
               description: "Debe ser un string y es obligatorio"
            },
            price: {
               bsonType: "number",
               minimum: 0,
               description: "Debe ser un numero positivo y es obligatorio"
            },
            category: {
               bsonType: "string"
            },
            stock: {
               bsonType: "int",
               minimum: 0,
               description: "Stock disponible"
            },
            attributes: {
               bsonType: "object",
               description: "Atributos flexibles del producto (color, talla, especificaciones)"
            }
         }
      }
   }
});

db.audit_logs.drop();
db.createCollection("audit_logs", {
   capped: true,
   size: 5242880,
   max: 5000
});

db.products.createIndex({ name: "text", description: "text" });
db.products.createIndex({ category: 1 });

//Datos de prueba
db.products.insertMany([
   // Electronics
   {
      name: "Laptop Gamer X1",
      price: 1500.00,
      category: "Electronics",
      stock: NumberInt(10),
      attributes: {
         ram: "16GB",
         processor: "Intel i7",
         gpu: "RTX 3060"
      }
   },
   {
      name: "iPhone 14 Pro",
      price: 999.00,
      category: "Electronics",
      stock: NumberInt(25),
      attributes: {
         storage: "256GB",
         color: "Space Black",
         screen: "6.1 inches"
      }
   },
   {
      name: "Samsung Galaxy Tab S8",
      price: 649.00,
      category: "Electronics",
      stock: NumberInt(15),
      attributes: {
         storage: "128GB",
         screen: "11 inches",
         stylus: "S Pen included"
      }
   },
   {
      name: "AirPods Pro 2",
      price: 249.00,
      category: "Electronics",
      stock: NumberInt(50),
      attributes: {
         noise_cancellation: "Active",
         battery: "6 hours",
         case: "MagSafe"
      }
   },
   {
      name: "Apple Watch Series 8",
      price: 399.00,
      category: "Electronics",
      stock: NumberInt(30),
      attributes: {
         size: "45mm",
         connectivity: "GPS + Cellular",
         sensors: "Heart rate, ECG, Blood oxygen"
      }
   },

   // Clothing
   {
      name: "Camiseta Developer",
      price: 25.50,
      category: "Clothing",
      stock: NumberInt(100),
      attributes: {
         size: ["S", "M", "L", "XL"],
         material: "Cotton",
         color: "Black"
      }
   },
   {
      name: "Sudadera Tech Pro",
      price: 45.00,
      category: "Clothing",
      stock: NumberInt(60),
      attributes: {
         size: ["S", "M", "L", "XL", "XXL"],
         material: "Cotton blend",
         color: "Navy Blue"
      }
   },
   {
      name: "Jeans Slim Fit",
      price: 59.99,
      category: "Clothing",
      stock: NumberInt(40),
      attributes: {
         size: ["28", "30", "32", "34", "36"],
         fit: "Slim",
         color: "Dark Blue"
      }
   },
   {
      name: "Zapatillas Running Pro",
      price: 89.00,
      category: "Clothing",
      stock: NumberInt(35),
      attributes: {
         size: ["7", "8", "9", "10", "11"],
         type: "Running",
         color: "White/Blue"
      }
   },

   // Home
   {
      name: "Lámpara LED Inteligente",
      price: 35.00,
      category: "Home",
      stock: NumberInt(45),
      attributes: {
         connectivity: "WiFi",
         colors: "16 million",
         voice_control: "Alexa, Google"
      }
   },
   {
      name: "Silla Ergonómica Office",
      price: 199.00,
      category: "Home",
      stock: NumberInt(20),
      attributes: {
         material: "Mesh",
         adjustable: "Height, armrests, lumbar",
         weight_capacity: "300 lbs"
      }
   },
   {
      name: "Escritorio Ajustable",
      price: 349.00,
      category: "Home",
      stock: NumberInt(12),
      attributes: {
         type: "Standing desk",
         size: "60x30 inches",
         motor: "Electric"
      }
   },

   // Books
   {
      name: "Clean Code",
      price: 42.00,
      category: "Books",
      stock: NumberInt(50),
      attributes: {
         author: "Robert C. Martin",
         pages: 464,
         language: "English"
      }
   },
   {
      name: "The Pragmatic Programmer",
      price: 45.00,
      category: "Books",
      stock: NumberInt(40),
      attributes: {
         author: "Andrew Hunt, David Thomas",
         pages: 352,
         language: "English"
      }
   },
   {
      name: "Design Patterns",
      price: 54.00,
      category: "Books",
      stock: NumberInt(30),
      attributes: {
         author: "Gang of Four",
         pages: 416,
         language: "English"
      }
   },

   // Sports
   {
      name: "Mancuernas Ajustables 20kg",
      price: 79.00,
      category: "Sports",
      stock: NumberInt(25),
      attributes: {
         weight: "20kg per pair",
         adjustable: "Yes",
         material: "Steel"
      }
   },
   {
      name: "Yoga Mat Premium",
      price: 29.00,
      category: "Sports",
      stock: NumberInt(55),
      attributes: {
         thickness: "6mm",
         material: "TPE",
         size: "183x61 cm"
      }
   },
   {
      name: "Bicicleta Estática",
      price: 299.00,
      category: "Sports",
      stock: NumberInt(8),
      attributes: {
         resistance: "Magnetic",
         display: "LCD",
         max_weight: "120kg"
      }
   }
]);

print("Base de datos MongoDB inicializada con éxito");
print(db.products.count() + " productos insertados");
