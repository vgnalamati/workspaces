package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
)

type User struct {
	Name  string `json:"name"`
	Id    int    `json:"id"`
	Home  string `json:"home"`
	Shell string `json:"shell"`
}

func main() {
	path, format := parse_flags()
	users := collect_users()

	var output io.Writer

	if path != "" {
		f, err := os.Create(path)
		handleError(err)
		defer f.Close()
		output = f
	} else {
		output = os.Stdout
	}

	if format == "json" {
		data, err := json.MarshalIndent(users, "", "  ")
		handleError(err)
		output.Write(data)
	}
}

func parse_flags() (path, format string) {
	flag.StringVar(&path, "path", "", "Path to the File")
	flag.StringVar(&format, "format", "json", "Output format")
	flag.Parse()

	format = strings.ToLower(format)

	if format != "json" {
		fmt.Println("Error: Invalid input format")
		flag.Usage()
		os.Exit(1)
	}

	return
}

func collect_users() (users []User) {
	file, err := os.Open("/etc/passwd")
	handleError(err)
	defer file.Close()

	reader := csv.NewReader(file)
	reader.Comma = ':'

	lines, err := reader.ReadAll()
	handleError(err)

	for _, line := range lines {
		id, err := strconv.ParseInt(line[2], 10, 64)
		handleError(err)

		if id < 1000 {
			continue
		}
		user := User{
			Name:  line[0],
			Id:    int(id),
			Home:  line[5],
			Shell: line[6],
		}

		users = append(users, user)
	}

	return
}

func handleError(error_type error) {
	if error_type != nil {
		fmt.Println("Error:", error_type)
		os.Exit(1)
	}
}
