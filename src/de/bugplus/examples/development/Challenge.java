package de.bugplus.examples.development;

import de.bugplus.development.*;
import de.bugplus.specification.BugplusLibrary;
import de.bugplus.specification.BugplusProgramSpecification;

import java.util.LinkedList;
import java.util.List;

public class Challenge {
    public static void main(String[] args){
        BugplusLibrary myFunctionLibrary = BugplusLibrary.getInstance();
        BugplusNEGImplementation negImpl = BugplusNEGImplementation.getInstance();
        myFunctionLibrary.addSpecification(negImpl.getSpecification());

        //CODE HERE
		BugplusProgramSpecification T2_Code_specification = BugplusProgramSpecification.getInstance("T2_Code_Instance", 0, 2, myFunctionLibrary); 
		BugplusProgramImplementation T2_Code_Implementation = T2_Code_specification.addImplementation();
		T2_Code_Implementation.addBug("!", "!_0");
		T2_Code_Implementation.addDataFlow("!_0", "!_0", 0);
		T2_Code_Implementation.connectControlInInterface("!_0");
		T2_Code_Implementation.addControlFlow("!_0", 0, "!_0");
		T2_Code_Implementation.addControlFlow("!_0", 1, "!_0");
		BugplusInstance challengeInstance = T2_Code_Implementation.instantiate();
		BugplusProgramInstanceImpl T2_Code_Instance_Impl = challengeInstance.getInstanceImpl();
		T2_Code_Instance_Impl.getBugs().get("!_0").setInternalState(0);
		BugplusThread newThread = BugplusThread.getInstance();
		newThread.connectInstance(challengeInstance);
		newThread.start();
		LinkedList<String> challengeBugs = new LinkedList<String>();
		System.out.println("Internal State " + "!_0" + ": 	" + T2_Code_Instance_Impl.getBugs().get("!_0").getInternalState());
		System.out.println("Call Counter " + "!_0" + ": 	" + T2_Code_Instance_Impl.getBugs().get("!_0").getCallCounter() + "\n");
    }
}
