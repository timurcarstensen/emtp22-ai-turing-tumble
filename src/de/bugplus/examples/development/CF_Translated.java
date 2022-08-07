package de.bugplus.examples.development;

import de.bugplus.development.*;
import de.bugplus.specification.BugplusLibrary;
import de.bugplus.specification.BugplusProgramSpecification;

public class CF_Translated {
    private static int[] execTimes;

    public static int[] execute(int num_bugs, int[][] cfMatrix, int[] positions) {
        BugplusLibrary myFunctionLibrary = BugplusLibrary.getInstance();
        BugplusNEGImplementation negImpl = BugplusNEGImplementation.getInstance();
        myFunctionLibrary.addSpecification(negImpl.getSpecification());

        //CODE HERE
        BugplusProgramSpecification CF_Translate_Specification = BugplusProgramSpecification.getInstance("CF_Translate", 0, 2, myFunctionLibrary);
        BugplusProgramImplementation cft_impl = CF_Translate_Specification.addImplementation();
        for (int i = 0; i < num_bugs; i++) {
            String bugId = "!_" + i;
            cft_impl.addBug("!", bugId);
            cft_impl.addDataFlow(bugId, bugId, 0);
        }


        for (int i = 0; i < cfMatrix.length; i++) {
            for (int j = 0; j < cfMatrix[0].length; j++) {
                if (cfMatrix[i][j] == 1) {
                    cft_impl.addControlFlow("!_" + (j / 2), j % 2, "!_" + i);
                }
            }
        }
        cft_impl.connectControlInInterface("!_0");
        BugplusInstance cftInstance = cft_impl.instantiate();
        BugplusProgramInstanceImpl cft_instance_impl = cftInstance.getInstanceImpl();
        BugplusThread newThread = BugplusThread.getInstance();
        newThread.connectInstance(cftInstance);

        //set internal states
        for (int i = 0; i < num_bugs; i++) {
            cft_instance_impl.getBugs().get("!_" + i).setInternalState(positions[i]);
        }

        newThread.start();
        int[] internalStates = new int[num_bugs];
        execTimes = new int[num_bugs];

        for (int i = 0; i < num_bugs; i++) {
            internalStates[i] = cft_instance_impl.getBugs().get("!_" + i).getInternalState();
            execTimes[i] = cft_instance_impl.getBugs().get("!_" + i).getCallCounter();
        }
        return internalStates;
    }

    public static int[] execute(int num_bugs, int[][] cfMatrix) {
        BugplusLibrary myFunctionLibrary = BugplusLibrary.getInstance();
        BugplusNEGImplementation negImpl = BugplusNEGImplementation.getInstance();
        myFunctionLibrary.addSpecification(negImpl.getSpecification());

        //CODE HERE
        BugplusProgramSpecification CF_Translate_Specification = BugplusProgramSpecification.getInstance("CF_Translate", 0, 2, myFunctionLibrary);
        BugplusProgramImplementation cft_impl = CF_Translate_Specification.addImplementation();
        for (int i = 0; i < num_bugs; i++) {
            String bugId = "!_" + i;
            cft_impl.addBug("!", bugId);
            cft_impl.addDataFlow(bugId, bugId, 0);
        }
		/*
		for i in range(self.N):
            for j in range(2 * self.N):
                if self.cfMatrix[i, j] == 1:
                    self.write_to_file(
                        f'cft_impl.addControlFlow("!_{int(j / 2)}", {j % 2}, "!_{i}");'
                    )
		 */


        for (int i = 0; i < cfMatrix.length; i++) {
            for (int j = 0; j < cfMatrix[0].length; j++) {
                if (cfMatrix[i][j] == 1) {
                    cft_impl.addControlFlow("!_" + (j / 2), j % 2, "!_" + i);
                }
            }
        }
        cft_impl.connectControlInInterface("!_0");
        BugplusInstance cftInstance = cft_impl.instantiate();
        BugplusProgramInstanceImpl cft_instance_impl = cftInstance.getInstanceImpl();
        BugplusThread newThread = BugplusThread.getInstance();
        newThread.connectInstance(cftInstance);
        newThread.start();
        int[] internalStates = new int[num_bugs];
        execTimes = new int[num_bugs];

        for (int i = 0; i < num_bugs; i++) {
            internalStates[i] = cft_instance_impl.getBugs().get("!_" + i).getInternalState();
            execTimes[i] = cft_instance_impl.getBugs().get("!_" + i).getCallCounter();
        }
        return internalStates;

    }

    public static boolean isZeroConnectionValid(int[][] cfMatrix, int pos) {
//        int wrongConnections = 0;
        for (int i = 0; i < cfMatrix.length * 2; i++) {
            if (cfMatrix[pos][i] != 0) {
                return false;
//                wrongConnections++;
            }
        }
        for (int i = 0; i < cfMatrix.length; i++) {
            if (cfMatrix[i][2 * pos] != 0) {
                return false;
//                wrongConnections++;
            }
            if (cfMatrix[i][2 * pos + 1] != 0) {
                return false;
//                wrongConnections++;
            }
        }
        return true;
//        return wrongConnections;
    }

    public static float obtain_reward(int[] bit_specification, int[][] cfMatrix, float Exec_Win_Reward, float Exec_Failure_Reward, float Exec_Partial_Correct_Reward) {
        //System.out.println("Partial " + Exec_Partial_Correct_Reward);
        //System.out.println("WIN: " + Exec_Win_Reward);
//        System.out.println("BITSPEC_CF");
//        System.out.println(bit_specification);
        //System.out.println(Arrays.toString(bit_specification));
        //for (int[] i : cfMatrix) {
        //System.out.println(Arrays.toString(i));
        //}
        //System.out.println(cfMatrix);
        float reward = 0;
        try {
            int[] internalStates = execute(cfMatrix.length, cfMatrix);
//            System.out.println("BITSPEC: " + bit_specification[0] + " " + bit_specification[1] + " " + bit_specification[2]);
//            System.out.println("Internal State: " + internalStates[0] + " " + internalStates[1] + " " + internalStates[2]);
            //reward = 0;
            boolean same_arrays = true;
            //self.bugs = 5 [0 1 2 0]

            for (int i = 0; i < bit_specification.length; i++) {
                if (bit_specification[i] == -1) {
                    if (execTimes[i] > 0) {
                        reward += Exec_Partial_Correct_Reward;
                    } else {
                        same_arrays = false;
                    }
                    //System.out.println("-1-1-1-1-1--1-1-1-");
                } else if (bit_specification[i] == 0) {
                    //System.out.println("0000000000000");
                    if (execTimes[i] == 0) {
                        reward += Exec_Partial_Correct_Reward;
                    } else {
                        same_arrays = false;
                    }

                } else if (bit_specification[i] != internalStates[i] + 1) {

                    //reward -= 20;
                    same_arrays = false;
                } else {
                    if (execTimes[i] > 0) {
                        reward += Exec_Partial_Correct_Reward;
                    } else {
                        same_arrays = false;
                    }
                    // bit_specification[i] == internalStates[i]
                    //reward += 1;
                }
            }
            //give high reward if correct
            if (same_arrays) {
                reward += Exec_Win_Reward;
                // System.out.println("Solved");
            }
//            System.out.println("REWARD: " + reward);
//            System.out.println("------------------------------------");
        } catch (IllegalStateException ise) {
            //System.out.println("Illegal State Exception: " + ise.toString());
            reward = Exec_Failure_Reward;
        } catch (StackOverflowError soe) {
            //System.out.println("Stack Overflow Error: " + soe.toString());
            reward = Exec_Failure_Reward;
        }
        //System.out.println(reward);
        return reward;
    }

    public static void main(String[] args) {
        int[] bitSpec = {1, 1, 1};
        int[][] cfMatrix = {{1, 1, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0, 0}};
        float reward = obtain_reward(bitSpec, cfMatrix, 1000, -10, 1);
        //System.out.println(reward);
    }
}