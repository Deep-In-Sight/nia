package com.lodong.android.eyetrackingtest;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import com.lodong.android.eyetrackingtest.model.Storage;
import com.lodong.android.eyetrackingtest.model.TestInfo;
import com.lodong.android.eyetrackingtest.model.User;

public class LoginActivity extends AppCompatActivity {
    private final String TAG = LoginActivity.class.getSimpleName();
    private final String MAN = "남성";
    private final String WOMAN = "여성";
    private EditText edtName, edtBirth;
    private RadioGroup rdgSex;
    private RadioButton rdbMan, rdbWoman;
    private LinearLayout linearNext;
    private TextView txtBack;
    private ImageView imgBack;

    private int userName=-99;
    private String userBirth="";
    private String userSex="";

    private final String USER = "user";
    private final String TEST_INFO = "test_info";
    private final String STORAGE = "storage";

    @Override
    public void onSaveInstanceState(@NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putSerializable(USER, User.getInstance());
        outState.putSerializable(TEST_INFO, TestInfo.getInstance());
        outState.putSerializable(STORAGE, Storage.getInstance());
    }

    @Override
    protected void onRestoreInstanceState(@NonNull Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        User.setInstance((User) savedInstanceState.getSerializable(USER));
        TestInfo.setInstance((TestInfo) savedInstanceState.getSerializable(TEST_INFO));
        Storage.setInstance((Storage) savedInstanceState.getSerializable(STORAGE));
    }
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        initValue();

        setOnClickListener();
    }

    private void initValue(){
        edtName = findViewById(R.id.edt_name);
        edtBirth = findViewById(R.id.edt_birth);
        rdgSex = findViewById(R.id.rdg_sex);
        rdbMan= findViewById(R.id.rdb_man);
        rdbWoman = findViewById(R.id.rdb_woman);
        linearNext = findViewById(R.id.linear_next);
        imgBack = findViewById(R.id.img_back);
        txtBack = findViewById(R.id.txt_back);
    }

    private void setOnClickListener(){
        rdgSex.setOnCheckedChangeListener((radioGroup, i) -> {
            switch (i){
                case R.id.rdb_man:
                    userSex = MAN;
                    break;
                case R.id.rdb_woman:
                    userSex = WOMAN;
                    break;
            }
        });

        linearNext.setOnClickListener(view -> {
            userName = Integer.parseInt(edtName.getText().toString().trim());
            userBirth = edtBirth.getText().toString();

            if(userName==-99 || userBirth.equals("") || userSex.equals("")){
                Toast.makeText(getApplicationContext(), "값을 모두 입력해주세요", Toast.LENGTH_SHORT).show();
            }else{
                User user = User.getInstance();
                user.setName(String.format("%03d", userName));
                user.setBirth(userBirth.trim());
                user.setSex(userSex);
                Log.d(TAG, userName + " "+ userBirth + " "+userSex);
                startActivity(new Intent(getApplicationContext(), SelectTestScenarioNumber.class));
            }
        });

        imgBack.setOnClickListener(view -> onBackPressed());

        txtBack.setOnClickListener(view -> onBackPressed());
    }
}