package main

import (
	"log"

	"reu-backend/internal/handlers"
	"reu-backend/internal/routes"

	"reu-backend/internal/models"

	"github.com/gin-gonic/gin"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func main() {
	// Initialize router
	router := gin.Default()

	// Initialize database
	db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	db.AutoMigrate(&models.User{})

	// Initialize handlers
	userHandler := handlers.NewUserHandler(db)
	utilsHandler := handlers.NewUtilsHandler(db)

	// Setup routes
	routes.SetupUserRoutes(router, userHandler)
	routes.SetupUtilsRoutes(router, utilsHandler)

	// Start server
	if err := router.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
