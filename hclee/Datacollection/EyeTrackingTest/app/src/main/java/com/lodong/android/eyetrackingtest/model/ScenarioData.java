package com.lodong.android.eyetrackingtest.model;

public class ScenarioData {
    private final static int[] focusPath = {3, 3, 3, 3, 3, 3, 3, 3, 3, 3};
    private final static int[] concentrationDeficiencyOrNegligencePath = {12, 12, 12, 12, 12, 12, 12, 12, 12, 12};
    private final static int[][] sleepinessOrDropInConcentrationPath ={
            {7, 7, 7, 7, 7, 7, 7, 7, 7, 7},
            {6, 6, 6, 6, 6, 6, 6, 6, 6, 6},
            {10, 10, 10, 10, 10, 8, 8, 8, 8, 8},
            {8, 8, 8, 8, 8, 10, 10, 10, 10, 10},
            {11, 11, 11, 11, 11, 16, 16, 16, 16, 16},
            {16, 16, 16, 16, 16, 11, 11, 11, 11, 11},
            {17, 17, 17, 17, 17, 17, 9, 9, 9, 9},
            {13, 13, 13, 13, 13, 18, 18, 18, 18, 18},
            {20, 20, 20, 21, 21, 21, 22, 22, 22, 22},
            {23, 23, 23, 24, 24, 24, 25, 25, 25, 25}
    };

    public static int[] getFocusPath() {
        return focusPath;
    }

    public static int[] getConcentrationDeficiencyOrNegligencePath() {
        return concentrationDeficiencyOrNegligencePath;
    }

    public static int[][] getSleepinessOrDropInConcentrationPath() {
        return sleepinessOrDropInConcentrationPath;
    }
}
