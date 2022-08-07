/*
 * MIT License
 *
 * Bug+ Interpreter
 * Copyright (c) 2022 Christian Bartelt
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package de.bugplus.examples.development;

import de.bugplus.development.*;
import de.bugplus.specification.BugplusLibrary;
import de.bugplus.specification.BugplusProgramSpecification;

import java.util.LinkedList;
import java.util.List;

/**
 * @Author Christian Bartelt
 * @Date 27.01.22 21:59
 * @Version 0.0.1
 */
public class NegBugsBasicArithmetic {

    public static void createCoherentComponents(List<String> bugs, BugplusProgramImplementation impl) {
        for (String s1 : bugs) {
            for (String s2 : bugs) {
                impl.addDataFlow(s1, s2, 0);
            }
        }
    }

    public static void main(String[] args) {


        //Initialization of a new function library

        BugplusLibrary myFunctionLibrary = BugplusLibrary.getInstance();


        BugplusNEGImplementation negImpl = BugplusNEGImplementation.getInstance();
        myFunctionLibrary.addSpecification(negImpl.getSpecification());

        //Test Negation Node:
        BugplusProgramSpecification negTestSpec = BugplusProgramSpecification.getInstance("!0_Test", 0, 2, myFunctionLibrary);
        BugplusProgramImplementation negTestImpl = negTestSpec.addImplementation();


        negTestImpl.addBug("!", "!_001"); //-> internalState(bug) = 200 + dataIn(bug) = 200
        negTestImpl.addBug("!", "!_002");
        negTestImpl.addBug("!", "!_003");

        // System.out.println(negImpl.instantiate());

        LinkedList<String> bugids = new LinkedList<String>();
        bugids.add("!_001");
        bugids.add("!_002");
        bugids.add("!_003");
        negTestImpl.addBug("!", "!_004");
        negTestImpl.addControlFlow("!_001", 0, "!_002");
        negTestImpl.addControlFlow("!_001", 1, "!_003");
        //negTestImpl.addDataFlow("!_001", "!_001", 0);
        //negTestImpl.addDataFlow("!_002", "!_002", 0);
        //negTestImpl.addDataFlow("!_003", "!_003", 0);

        //Zahnraeder
        createCoherentComponents(bugids, negTestImpl);

        negTestImpl.connectControlInInterface("!_001");
        //negTestImpl.connectDataInInterface("!_001", 0, 0);
        //negTestImpl.connectDataInInterface("!_002", 0, 1);
        //negTestImpl.connectDataInInterface("!_003", 0, 2);
        //negTestImpl.connectDataOutInterface("!_001");
        negTestImpl.connectDataOutInterface("!_002");
        negTestImpl.connectDataOutInterface("!_003");
        negTestImpl.connectControlOutInterface("!_002", 0, 0);
        negTestImpl.connectControlOutInterface("!_002", 1, 1);
        negTestImpl.connectControlOutInterface("!_003", 0, 0);
        negTestImpl.connectControlOutInterface("!_003", 1, 1);


        /*BugplusInstance testInstance = negTestImpl.instantiate();
        BugplusProgramInstanceImpl test = (BugplusProgramInstanceImpl) testInstance;
        test.getBugs().get("!_001").setInternalState(0);
        test.getBugs().get("!_002").setInternalState(1);
        test.getBugs().get("!_003").setInternalState(1);
        test.getBugs().get("!_004").setInternalState(0);*/

        /*System.out.println("Starting State " + "!_001 : " + test.getBugs().get("!_001").getInternalState());
        System.out.println("Starting State " + "!_002 : " + test.getBugs().get("!_002").getInternalState());
        System.out.println("Starting State " + "!_003 : " + test.getBugs().get("!_003").getInternalState());
        System.out.println("Starting State " + "!_004 : " + test.getBugs().get("!_004").getInternalState()+"\n");


        System.out.println("Data Ins:");
        System.out.println("Data In " + "!_001 : " + test.getBugs().get("!_001").getDataInputs().get(0).getVariable().getValue());
        System.out.println("Data In " + "!_002 : " + test.getBugs().get("!_002").getDataInputs().get(0).getVariable().getValue());
        System.out.println("Data In " + "!_003 : " + test.getBugs().get("!_003").getDataInputs().get(0).getVariable().getValue());
        System.out.println("Data In " + "!_004 : " + test.getBugs().get("!_004").getDataInputs().get(0).getVariable().getValue() +"\n");
*/


        //Challenge 24
        BugplusProgramSpecification challenge24Spec = BugplusProgramSpecification.getInstance("ch24_Test", 0, 2, myFunctionLibrary);
        BugplusProgramImplementation challenge24Impl = challenge24Spec.addImplementation();
        //We need 4 Bits
        LinkedList<String> ch24bugs = new LinkedList<String>();
        for (int i = 1; i <= 4; i++) {
            String bugID = "!_00" + i;
            ch24bugs.add(bugID);
            challenge24Impl.addBug("!", bugID);

            //connect data out with data in for each bug
            challenge24Impl.addDataFlow(bugID, bugID, 0);
        }


        challenge24Impl.connectControlInInterface(ch24bugs.get(0));
        challenge24Impl.addControlFlow(ch24bugs.get(0), 0, ch24bugs.get(0));
        challenge24Impl.addControlFlow(ch24bugs.get(0), 1, ch24bugs.get(1));

        challenge24Impl.addControlFlow(ch24bugs.get(1), 0, ch24bugs.get(0));
        challenge24Impl.addControlFlow(ch24bugs.get(1), 1, ch24bugs.get(2));

        challenge24Impl.addControlFlow(ch24bugs.get(2), 0, ch24bugs.get(0));
        challenge24Impl.addControlFlow(ch24bugs.get(2), 1, ch24bugs.get(3));

        challenge24Impl.addControlFlow(ch24bugs.get(3), 0, ch24bugs.get(0));
        //challenge24Impl.addControlFlow(ch24bugs.get(3), 1, ch24bugs.get(1));

        challenge24Impl.connectControlOutInterface(ch24bugs.get(3), 1, 0);
        challenge24Impl.connectControlOutInterface(ch24bugs.get(3), 1, 1);


        challenge24Impl.connectDataOutInterface(ch24bugs.get(3));


        //Example
        BugplusProgramSpecification exampleSpec = BugplusProgramSpecification.getInstance("example", 0, 2, myFunctionLibrary);
        BugplusProgramImplementation exampleImpl = exampleSpec.addImplementation();

        exampleImpl.addBug("!", "!_01");
        exampleImpl.addBug("!", "!_02");
        exampleImpl.addBug("!", "!_03");


        exampleImpl.addDataFlow("!_01", "!_01", 0);
        exampleImpl.addDataFlow("!_02", "!_02", 0);
        exampleImpl.addDataFlow("!_03", "!_03", 0);

        exampleImpl.addControlFlow("!_01", 1, "!_01");
        exampleImpl.addControlFlow("!_01", 0, "!_02");

        exampleImpl.addControlFlow("!_02", 1, "!_01");
        exampleImpl.addControlFlow("!_02", 0, "!_03");

        exampleImpl.addControlFlow("!_03", 1, "!_01");
        //exampleImpl.addControlFlow("!_03", 0, "!_02");
        exampleImpl.connectControlInInterface("!_01");



        //Challenge 41
        BugplusProgramSpecification challenge41Spec = BugplusProgramSpecification.getInstance("ch41_Test", 0, 2, myFunctionLibrary);
        BugplusProgramImplementation challenge41Impl = challenge24Spec.addImplementation();




        //We need 8 Bits
        LinkedList<String> ch41bugs = new LinkedList<String>();

        //4 Register Bits + 4 Helper Bits
        for (int i = 0; i < 8; i++) {
            String bugID = "!_00" + i;
            ch41bugs.add(bugID);
            challenge41Impl.addBug("!", bugID);
        }
        for (int i = 0; i < 4; i++) {
            createCoherentComponents(ch41bugs.subList((i * 2), (i * 2 + 2)), challenge41Impl);
        }


        challenge41Impl.connectControlInInterface(ch41bugs.get(1));
        challenge41Impl.addControlFlow(ch41bugs.get(1), 0, ch41bugs.get(3));
        challenge41Impl.addControlFlow(ch41bugs.get(1), 1, ch41bugs.get(0));

        challenge41Impl.addControlFlow(ch41bugs.get(0), 0, ch41bugs.get(3));
        //challenge41Impl.addControlFlow(ch41bugs.get(0), 1, ch41bugs.get(2));

        challenge41Impl.addControlFlow(ch41bugs.get(3), 0, ch41bugs.get(4));
        challenge41Impl.addControlFlow(ch41bugs.get(3), 1, ch41bugs.get(2));

        challenge41Impl.addControlFlow(ch41bugs.get(2), 0, ch41bugs.get(4));
        //challenge41Impl.addControlFlow(ch41bugs.get(3), 1, ch41bugs.get(2));

        challenge41Impl.addControlFlow(ch41bugs.get(4), 0, ch41bugs.get(6));
        challenge41Impl.addControlFlow(ch41bugs.get(4), 1, ch41bugs.get(5));

        challenge41Impl.addControlFlow(ch41bugs.get(5), 0, ch41bugs.get(6));

        challenge41Impl.addControlFlow(ch41bugs.get(6), 1, ch41bugs.get(7));
        challenge41Impl.connectControlOutInterface(ch41bugs.get(6), 0, 0);
        challenge41Impl.connectControlOutInterface(ch41bugs.get(6), 0, 1);


        challenge41Impl.connectControlOutInterface(ch41bugs.get(7), 0, 0);
        challenge41Impl.connectControlOutInterface(ch41bugs.get(7), 0, 1);

        challenge41Impl.connectDataOutInterface(ch41bugs.get(6));
        challenge41Impl.connectDataOutInterface(ch41bugs.get(7));


// Application

        //Challenge 24
        BugplusInstance ch24Instance = challenge24Impl.instantiate();
        //BugplusProgramInstanceImpl ch24Test = (BugplusProgramInstanceImpl) ch24Instance;
        BugplusProgramInstanceImpl ch24Test = ch24Instance.getInstanceImpl();
        ch24Test.getBugs().get("!_001").setInternalState(1);
        ch24Test.getBugs().get("!_002").setInternalState(0);
        ch24Test.getBugs().get("!_003").setInternalState(0);
        ch24Test.getBugs().get("!_004").setInternalState(1);

        BugplusThread newThread = BugplusThread.getInstance();
        newThread.connectInstance(ch24Instance);


        newThread.start();
        //Override to correct internal state
        for (
                String s : ch24bugs) {
            //ch24Test.getBugs().get(s).setInternalState(ch24Test.getBugs().get(s).getDataInputs().get(0).getVariable().getValue());

            System.out.println("Internal State " + s + ": \t" + ch24Test.getBugs().get(s).getInternalState());
            System.out.println("Call Counter " + s + ": \t" + ch24Test.getBugs().get(s).getCallCounter() + "\n");
        }

        //Challenge 41
        BugplusInstance ch41Instance = challenge41Impl.instantiate();
        BugplusProgramInstanceImpl ch41Test = (BugplusProgramInstanceImpl) ch41Instance;
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                for (int k = 0; k < 2; k++) {
                    for (int l = 0; l < 2; l++) {
                        ch41Test.getBugs().get("!_000").setInternalState(i);
                        ch41Test.getBugs().get("!_002").setInternalState(j);
                        ch41Test.getBugs().get("!_004").setInternalState(k);
                        ch41Test.getBugs().get("!_006").setInternalState(l);

                        newThread = BugplusThread.getInstance();
                        newThread.connectInstance(ch41Instance);


                        newThread.start();
                        //Override to correct internal state
                        int count = 0;
                        for (
                                String s : ch41bugs) {
                            if (count % 2 == 0) {
                                ch41Test.getBugs().get(s).setInternalState(ch41Test.getBugs().get(s).getDataInputs().get(0).getVariable().getValue());

                                System.out.println("Internal State " + s + ": " + ch41Test.getBugs().get(s).getInternalState());
                            }
                            count++;
                        }
                    }
                }
            }
        }

        System.out.println("Example Challenge");
        //Example Challenge
        BugplusInstance exampleInstance = exampleImpl.instantiate();
        newThread= BugplusThread.getInstance();
        newThread.connectInstance(exampleInstance);
        newThread.start();
        BugplusProgramInstanceImpl exampleTest = exampleInstance.getInstanceImpl();


        System.out.println("Internal State " + "!_01" + ": \t" + exampleTest.getBugs().get("!_01").getInternalState());
        System.out.println("Call Counter " + "!_01" + ": \t" + exampleTest.getBugs().get("!_01").getCallCounter() + "\n");

        System.out.println("Internal State " + "!_02" + ": \t" + exampleTest.getBugs().get("!_02").getInternalState());
        System.out.println("Call Counter " + "!_02" + ": \t" + exampleTest.getBugs().get("!_02").getCallCounter() + "\n");

        System.out.println("Internal State " + "!_03" + ": \t" + exampleTest.getBugs().get("!_03").getInternalState());
        System.out.println("Call Counter " + "!_03" + ": \t" + exampleTest.getBugs().get("!_03").getCallCounter() + "\n");

    }
}
