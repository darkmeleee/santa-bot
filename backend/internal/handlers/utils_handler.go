package handlers

import (
	"math/rand"
	"net/http"
	"reu-backend/internal/models"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type UtilsHandler struct {
	DB *gorm.DB
}

func NewUtilsHandler(db *gorm.DB) *UtilsHandler {
	return &UtilsHandler{DB: db}
}

func (h *UtilsHandler) AssignSecretSantas(c *gin.Context) {
	var users []models.User
	result := h.DB.Find(&users)
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch users: " + result.Error.Error(),
		})
		return
	}

	if len(users) < 2 {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Need at least 2 users for secret santa assignment",
		})
		return
	}

	h.DB.Model(&models.User{}).Updates(map[string]interface{}{
		"giver_id":   nil,
		"reciver_id": nil,
	})

	shuffledUsers := make([]models.User, len(users))
	copy(shuffledUsers, users)

	rand.Seed(time.Now().UnixNano())
	rand.Shuffle(len(shuffledUsers), func(i, j int) {
		shuffledUsers[i], shuffledUsers[j] = shuffledUsers[j], shuffledUsers[i]
	})

	for i := 0; i < len(shuffledUsers); i++ {
		giver := shuffledUsers[i]
		receiver := shuffledUsers[(i+1)%len(shuffledUsers)]

		receiverID := receiver.TelegramID
		h.DB.Model(&giver).Update("reciver_id", &receiverID)
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Secret santas assigned successfully",
		"count":   len(users),
	})
}
