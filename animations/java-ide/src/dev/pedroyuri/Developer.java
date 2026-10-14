package dev.pedroyuri;

public class Developer {

    private final String name = "Pedro Yuri";
    private final String role = "Software Engineer";

    public void build() {
        System.out.println("Turning ideas into code.");
    }

    public static void main(String[] args) {
        new Developer().build();
    }
}
