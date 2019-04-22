package main

import (
    "fmt"
)

type Saiyan struct {
    Name string
    Age int
}


func main() {
    person := Saiyan {}
    value := [10]int{1, 2, 3, 4, 5, 6, 7, 8, 9, 0}
    scores := make([]int, 0, 10)

    person.Name = "Goutam"
    person.Age = 28

    fmt.Printf("Name: %s\nAge: %d\n", person.Name, person.Age)

    for index, value := range value {
        fmt.Printf("%d: %d\n", index, value)
    }
    fmt.Println()

    scores = append(scores, 5)
    fmt.Println(scores)
    fmt.Printf("Capacity of the list: %d\n", cap(scores))
    println("Done....")
}
