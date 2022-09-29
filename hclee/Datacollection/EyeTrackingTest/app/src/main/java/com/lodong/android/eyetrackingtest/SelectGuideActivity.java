package com.lodong.android.eyetrackingtest;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.lodong.android.eyetrackingtest.model.Storage;
import com.lodong.android.eyetrackingtest.model.TestInfo;
import com.lodong.android.eyetrackingtest.model.User;

public class SelectGuideActivity extends AppCompatActivity {
    private final String TAG = SelectGuideActivity.class.getSimpleName();
    private TextView txtStatus, txtCond1, txtCond2, txtCond3;
    private ImageView imgStatus, imgCheck1, imgCheck2, imgCheck3;
    private LinearLayout linearStart;
    private TextView txtBack;
    private ImageView imgBack;

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
        setContentView(R.layout.activity_select_guide);
        initView();
        setOnClickListener();
        settingView();
    }

    private void initView(){
        txtStatus = findViewById(R.id.txt_status);
        txtCond1 = findViewById(R.id.txt_cond_1);
        txtCond2 = findViewById(R.id.txt_cond_2);
        txtCond3 = findViewById(R.id.txt_cond_3);
        imgStatus = findViewById(R.id.img_status);
        linearStart = findViewById(R.id.linear_start);
        imgCheck1 = findViewById(R.id.img_check1);
        imgCheck2 = findViewById(R.id.img_check2);
        imgCheck3 = findViewById(R.id.img_check3);
        imgBack = findViewById(R.id.img_back);
        txtBack = findViewById(R.id.txt_back);
    }

    private void setOnClickListener(){
        linearStart.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), CheckDeviceActivity.class));
        });
        imgBack.setOnClickListener(view -> onBackPressed());
        txtBack.setOnClickListener(view -> onBackPressed());
    }

    private void settingView(){
        TestInfo testInfo = TestInfo.getInstance();
        txtStatus.setText(testInfo.getStatusString());
        switch (testInfo.getStatus()){
            case 0:
                imgStatus.setImageDrawable(getDrawable(R.drawable.cond1));
                break;
            case 1:
                imgStatus.setImageDrawable(getDrawable(R.drawable.cond2));
                break;
            case 2:
                imgStatus.setImageDrawable(getDrawable(R.drawable.cond3));
                break;
            case 3:
                imgStatus.setImageDrawable(getDrawable(R.drawable.cond4));
                break;
            case 4:
                imgStatus.setImageDrawable(getDrawable(R.drawable.cond5));
                break;
        }

        String[] cond_list = testInfo.getStatusCond()[testInfo.getStatus()];
        switch (cond_list.length){
            case 1:
                imgCheck2.setVisibility(View.INVISIBLE);
                imgCheck3.setVisibility(View.INVISIBLE);
                txtCond2.setVisibility(View.INVISIBLE);
                txtCond3.setVisibility(View.INVISIBLE);
                txtCond1.setText(cond_list[0]);
                break;
            case 2:
                imgCheck3.setVisibility(View.INVISIBLE);
                txtCond3.setVisibility(View.INVISIBLE);
                txtCond1.setText(cond_list[0]);
                txtCond2.setText(cond_list[1]);
                break;
            case 3:
                txtCond1.setText(cond_list[0]);
                txtCond2.setText(cond_list[1]);
                txtCond3.setText(cond_list[2]);
                break;
        }
    }
}