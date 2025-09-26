// MongoDB initialization script for development
db = db.getSiblingDB('class_management');

// Create collections with validation
db.createCollection('students', {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["student_id", "first_name", "last_name", "email", "enrollment_date"],
         properties: {
            student_id: {
               bsonType: "string",
               description: "must be a string and is required"
            },
            first_name: {
               bsonType: "string",
               description: "must be a string and is required"
            },
            last_name: {
               bsonType: "string",
               description: "must be a string and is required"
            },
            email: {
               bsonType: "string",
               pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
               description: "must be a valid email address and is required"
            },
            phone: {
               bsonType: ["string", "null"],
               description: "must be a string if provided"
            },
            date_of_birth: {
               bsonType: ["date", "null"],
               description: "must be a date if provided"
            },
            address: {
               bsonType: ["string", "null"],
               description: "must be a string if provided"
            },
            enrollment_date: {
               bsonType: "date",
               description: "must be a date and is required"
            },
            created_at: {
               bsonType: "date",
               description: "must be a date and is required"
            },
            updated_at: {
               bsonType: "date",
               description: "must be a date and is required"
            }
         }
      }
   }
});

// Create indexes for better performance
db.students.createIndex({ "student_id": 1 }, { unique: true });
db.students.createIndex({ "email": 1 }, { unique: true });
db.students.createIndex({ "first_name": 1, "last_name": 1 });
db.students.createIndex({ "enrollment_date": 1 });

// Insert sample data for development
db.students.insertMany([
   {
      student_id: "STU001",
      first_name: "John",
      last_name: "Doe",
      email: "john.doe@example.com",
      phone: "+1-555-0101",
      date_of_birth: new Date("2000-01-15"),
      address: "123 Main St, Anytown, USA",
      enrollment_date: new Date(),
      created_at: new Date(),
      updated_at: new Date()
   },
   {
      student_id: "STU002",
      first_name: "Jane",
      last_name: "Smith",
      email: "jane.smith@example.com",
      phone: "+1-555-0102",
      date_of_birth: new Date("1999-05-20"),
      address: "456 Oak Ave, Somewhere, USA",
      enrollment_date: new Date(),
      created_at: new Date(),
      updated_at: new Date()
   }
]);

print('MongoDB initialization completed for development environment');
print('Created collections: students');
print('Created indexes on: student_id, email, name, enrollment_date');
print('Inserted sample data: 2 students');