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

package de.bugplus.development;


import de.bugplus.specification.BugplusNEGSpecification;

/**
 * @Author Christian Bartelt
 * @Date 23.01.22 21:37
 * @Version 0.0.1
 */
public class BugplusNEGInstanceImpl extends AbstractBugplusInstance implements BugplusNEGInstance {

    //protected int callCounter;

    protected BugplusNEGInstanceImpl() {
        //this.callCounter = 0;
    }

    BugplusNEGInstanceImpl(BugplusImplementation implementation) {

        this.initializeImplementation(this, implementation);

        this.createInterface(1, 2);

        this.initializeInterface(this.getInterface());

        BugplusControlInPin controlInPin = BugplusControlInPin.getInstance(this);
        this.getInterface().setControlInput(controlInPin);

    }

    protected void initializeImplementation(BugplusNEGInstanceImpl instance, BugplusImplementation implementation) {

        implementation.setSpecification(BugplusNEGSpecification.getInstance(this.getImplementation()));
        instance.setImplementation(implementation);
    }

    protected void initializeInterface(BugplusInterface bugplusInterface) {

        bugplusInterface.getDataInputs().get(0).setVariable(BugplusVariable.getInstance(this.getInterface().getInternalState()));
        //System.out.println(this.getInterface().getInternalState());
        //bugplusInterface.getDataInputs().get(1).setVariable(BugplusVariable.getInstance(0));

        BugplusDataOutPin dataOutPin = BugplusDataOutPin.getInstance();
        dataOutPin.setVariable(BugplusVariable.getInstance(0));
        dataOutPin.setConnected();
        bugplusInterface.setDataOutputPin(dataOutPin);

        //bugplusInterface.getDataInputs().get(0).getVariable().setValue(this.getInterface().getInternalState());
    }


    @Override
    public void execute() {
        //this.callCounter++;
        //System.out.println("in exec internal State: " + this.getInterface().getInternalState());
        //System.out.println("Data in Value: " + this.getInterface().getDataInputs().get(0).getVariable().getValue());
        boolean b1 = this.getDataInputs().get(0).isConnected();
        //boolean b2 = this.getDataInputs().get(1).isConnected();

        int result = 0;
        /**
         if (!b1) {
         result = 1;
         } else if (b1 & !b2) {
         result = 1;
         } else if (!b1 & b2) {
         result = -1;
         } else {
         int summand1 = this.getInterface().getDataInputs().get(0).getVariable().getValue();
         int summand2 = this.getInterface().getDataInputs().get(1).getVariable().getValue();
         result = summand1 + summand2;
         }
         */


        if (this.getDataInputs().get(0).getVariable().getValue() != 0 && this.getDataInputs().get(0).getVariable().getValue() != 1) {
            throw new IllegalStateException("Wrong Data Input Value! Must be 0 or 1!");
        }
        result = this.getDataInputs().get(0).getVariable().getValue() == 1 ? 0 : 1;
        this.getInterface().setInternalState(result);
        this.getInterface().setCallCounter(this.getInterface().getCallCounter() + 1);

        if(this.getInterface().getCallCounter() >= 20){
            throw new IllegalStateException("Too many Bugcalls!");
        }

        BugplusDataOutPin dataOutPin = this.getDataOut();

        if (dataOutPin.getVariable() == null) {
            dataOutPin.setVariable(BugplusVariable.getInstance());
        }

        dataOutPin.getVariable().setValue(result);

        dataOutPin.updateInterfaceOutput();

        if (result == 0) {
            this.getInterface().getControlOutputs().get(0).execute();
        } else {
            this.getInterface().getControlOutputs().get(1).execute();
        }
    }

    @Override
    public void unsetPins() {
        // do not implement
    }

}
