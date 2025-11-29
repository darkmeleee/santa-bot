package models

import (
	"gorm.io/gorm"
)

type EnumRole string

const (
	RoleAdmin EnumRole = "admin"
	RoleUser  EnumRole = "user"
)

type User struct {
	gorm.Model
	TelegramID   string   `json:"telegram_id" gorm:"primaryKey, unique"`
	TelegramName string   `json:"telegram_name"`
	Wishes       string   `json:"wishes"`
	Name         string   `json:"name" gorm:"not null"`
	Surname      string   `json:"surname" gorm:"not null"`
	Group        string   `json:"group" gorm:"not null"`
	Photo        string   `json:"photo"`
	ReciverID    *string  `json:"reciver_id"`
	Reciver      *User    `json:"reciver,omitempty" gorm:"foreignKey:ReciverID;references:TelegramID"`
	GiverID      *string  `json:"giver_id"`
	Giver        *User    `json:"giver,omitempty" gorm:"foreignKey:GiverID;references:TelegramID"`
	Role         EnumRole `json:"role"`
}
