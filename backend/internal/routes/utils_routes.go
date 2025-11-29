package routes

import (
	"reu-backend/internal/handlers"

	"github.com/gin-gonic/gin"
)

func SetupUtilsRoutes(router *gin.Engine, utilsHandler *handlers.UtilsHandler) {
	utilsGroup := router.Group("/utils")
	{
		utilsGroup.POST("/assign-secret-santas", utilsHandler.AssignSecretSantas)
	}
}
