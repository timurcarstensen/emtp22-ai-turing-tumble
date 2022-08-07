package de.bugplus.examples.development;

import de.bugplus.development.*;
import de.bugplus.specification.BugplusLibrary;
import de.bugplus.specification.BugplusProgramSpecification;

public class Bugplus_Translator_newSpec {
    private static int[] execTimes;


    public static int[] execute(int numBugs, int[][] cfMatrix, int[][] dfMatrix, int[][] spec_input) {
        BugplusLibrary myFunctionLibrary = BugplusLibrary.getInstance();
        BugplusADDImplementation addImpl = BugplusADDImplementation.getInstance();
        myFunctionLibrary.addSpecification(addImpl.getSpecification());

        BugplusProgramSpecification Program = BugplusProgramSpecification.getInstance("bug_program", 2, 2, myFunctionLibrary);
        myFunctionLibrary.addSpecification(Program);
        BugplusProgramImplementation program_impl = Program.addImplementation();
        for (int i = 0; i < numBugs; i++) {
            String bugId = "+_" + i;
            program_impl.addBug("+", bugId);
            //System.out.println("Add Bug " + bugId);
            //qm_impl.addDataFlow(bugId, bugId, 0);
        }


        for (int i = 0; i < cfMatrix.length - 2; i++) {
            for (int j = 0; j < cfMatrix[0].length - 1; j++) {
                if (cfMatrix[i][j] == 1) {
                    program_impl.addControlFlow("+_" + (j / 2), j % 2, "+_" + i);
                    //System.out.println("addControlFlow( +_" + (j / 2) + " , " + j % 2 + " , " + "+_" + i + ")");
                }
            }
        }


        //C_Out Interfaces:
        for (int i = cfMatrix.length - 2; i < cfMatrix.length; i++) {
            for (int j = 0; j < cfMatrix[0].length - 1; j++) {  //last column means we connect in-interface directly to out-interface
                if (cfMatrix[i][j] == 1) {
                    program_impl.connectControlOutInterface("+_" + (j / 2), j % 2, i == cfMatrix.length - 2 ? 0 : 1);
                    //System.out.println("connectControlOutInterface(+_ " + (j / 2) + " , " + (j % 2) + " , " + (i == cfMatrix.length - 2 ? 0 : 1) + ")");
                }
            }
        }

        //C_In Interface:
        for (int i = 0; i < cfMatrix.length; i++) {
            if (cfMatrix[i][cfMatrix[0].length - 1] == 1) {
                if (i != cfMatrix.length - 1 && i != cfMatrix.length - 2) { // last two rows means we connect in-interface directly to out-interface
                    program_impl.connectControlInInterface("+_" + (i));
                    //System.out.println("connectControlInInterface(+_ " + (i) + ")");
                } //else
                //System.out.println("Can't connect in-interface to out-interface");
            }
        }


        //DataFlow Matrix:
        for (int i = 0; i < dfMatrix.length - 1; i++) {
            for (int j = 0; j < dfMatrix[0].length - 2; j++) {
                if (dfMatrix[i][j] == 1) {
                    program_impl.addDataFlow("+_" + j, "+_" + (i / 2), i % 2);
                    //System.out.println("addDataFlow(+_ " + j + " , +_" + (i / 2) + " , " + i % 2 + ")");
                }
            }
        }


        //D_IN Interfaces:
        for (int i = 0; i < dfMatrix.length - 1; i++) {
            for (int j = dfMatrix[0].length - 2; j < dfMatrix[0].length; j++) {
                if (dfMatrix[i][j] == 1) {
                    program_impl.connectDataInInterface("+_" + (i / 2), i % 2, j == dfMatrix[0].length - 2 ? 0 : 1);
                    //System.out.println("connectDataInInterface(+_" + (i / 2) + " , " + i % 2 + " , " + (j == dfMatrix[0].length - 2 ? 0 : 1) + ")");
                }
            }
        }

        //D_OUT Interface:
        for (int j = 0; j < dfMatrix[0].length; j++) {
            if (dfMatrix[dfMatrix.length - 1][j] == 1) {
                if (j < dfMatrix[0].length - 2) { //last row means we connect in-interface directly to out-interface
                    program_impl.connectDataOutInterface("+_" + (j));
                    //System.out.println("connectDataOutInterface(+_" + j + ")");
                }// else
                //System.out.println("Can't connect DataIn-interface to DataOut-interface");
            }
        }


        BugplusInstance cftInstance = program_impl.instantiate();
        BugplusProgramInstanceImpl cft_instance_impl = cftInstance.getInstanceImpl();
        BugplusThread newThread = BugplusThread.getInstance();
        newThread.connectInstance(cftInstance);

        int diff = 0;
        int[] outputs = new int[spec_input.length];

        for (int i = 0; i < spec_input.length; i++) {
            cftInstance.setInputValue(0, spec_input[i][0]);
            cftInstance.setInputValue(1, spec_input[i][1]);

            newThread.start();
            outputs[i] = cftInstance.getOutputValue();


//            System.out.println(cftInstance.getOutputValue());
        }


        return outputs;

    }

    public static void main(String[] args) {
        int[] bitSpec = {1, 1, 1};
        int[][] cfMatrix = {
                {0, 0, 1},
                {1, 0, 0},
                {0, 1, 0}
        };
        //      Out1  Out2  CIN
        //BitIN
        //COut1
        //COut2
        int[][] dfMatrix = {
                {0, 1, 0},
                {0, 0, 1},
                {1, 0, 0}
        };

        //      BitOut DIN1 DIN2
        //BitIN1
        //BitIn2
        //ROut
        int[][] specInput = {{1, 1}, {2, 3}, {4, 5}};
        int[] outs = execute(1, cfMatrix, dfMatrix, specInput);
        for (int i : outs) {
            System.out.println(i);
        }
    }
}