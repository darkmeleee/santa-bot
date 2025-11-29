package routes

import (
	"reu-backend/internal/handlers"

	"github.com/gin-gonic/gin"
)

func SetupUserRoutes(router *gin.Engine, userHandler *handlers.UserHandler) {
	userGroup := router.Group("/user")
	{
		userGroup.GET("/:id", userHandler.GetUser)
		userGroup.GET("", userHandler.GetUsers)
		userGroup.POST("", userHandler.CreateUser)
		userGroup.PUT("/:id", userHandler.UpdateUser)
		userGroup.DELETE("/:id", userHandler.DeleteUser)
		userGroup.GET("/admin/:id", userHandler.CheckAdmin)
		userGroup.GET("/count", userHandler.GetUserCount)
		userGroup.DELETE("", userHandler.DeleteAllUsers)
	}
}
