package handlers

import (
	"net/http"

	"reu-backend/internal/models"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type UserHandler struct {
	DB *gorm.DB
}

func NewUserHandler(db *gorm.DB) *UserHandler {
	return &UserHandler{DB: db}
}

func (h *UserHandler) GetUser(c *gin.Context) {
	var user models.User
	result := h.DB.Preload("Reciver").Preload("Giver").Where("telegram_id = ?", c.Param("id")).First(&user)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, gin.H{
				"error": "User not found",
			})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": result.Error.Error(),
			})
		}
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"message": "User details endpoint",
		"user":    user,
	})

}

func (h *UserHandler) GetUserCount(c *gin.Context) {
	var count int64
	h.DB.Count(&count)
	c.JSON(http.StatusOK, gin.H{
		"message": "User count endpoint",
		"count":   count,
	})
}

func (h *UserHandler) CreateUser(c *gin.Context) {
	var user models.User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": err.Error(),
		})
		return
	}

	var existingUser models.User
	checkResult := h.DB.Where("telegram_id = ?", user.TelegramID).First(&existingUser)
	if checkResult.Error == nil {
		c.JSON(http.StatusConflict, gin.H{
			"error": "User with this telegram_id already exists",
		})
		return
	}

	result := h.DB.Create(&user)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": result.Error.Error(),
		})
		return
	}

	h.DB.Preload("Reciver").Preload("Giver").First(&user, user.TelegramID)

	c.JSON(http.StatusCreated, gin.H{
		"message": "User created",
		"user":    user,
	})
}

func (h *UserHandler) UpdateUser(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "User updated",
	})
}

func (h *UserHandler) DeleteUser(c *gin.Context) {
	result := h.DB.Where("telegram_id = ?", c.Param("id")).Delete(&models.User{})
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": result.Error.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "User deleted",
		"result":  result,
	})
}

func (h *UserHandler) GetUsers(c *gin.Context) {
	var users []models.User
	result := h.DB.Preload("Reciver").Preload("Giver").Find(&users)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": result.Error.Error(),
		})
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"message": "Users list endpoint",
		"users":   users,
	})
}

func (h *UserHandler) DeleteAllUsers(c *gin.Context) {
	result := h.DB.Where("1 = 1").Delete(&models.User{})
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": result.Error.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "All users deleted successfully",
		"count":   result.RowsAffected,
	})
}

func (h *UserHandler) CheckAdmin(c *gin.Context) {
	var user models.User
	result := h.DB.Where("telegram_id = ?", c.Param("id")).First(&user)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": result.Error.Error(),
		})
		return
	}

	if user.Role != "admin" {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "User is not an admin",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "User is an admin",
	})
}
