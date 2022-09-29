package com.lodong.android.eyetrackingtest.model;

import java.io.Serializable;

public class User implements Serializable {
    private static User instance;
    private String device_type;
    private String name;
    private String birth;
    private String sex;

    private User() {}

    public static User getInstance(){
        if(instance == null){
            instance = new User();
        }

        return instance;
    }

    public String getDevice_type() {
        return device_type;
    }

    public void setDevice_type(String device_type) {
        this.device_type = device_type;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getBirth() {
        return birth;
    }

    public void setBirth(String birth) {
        this.birth = birth;
    }

    public String getSex() {
        return sex;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }

    public static void setInstance(User instance) {
        User.instance = instance;
    }
}
