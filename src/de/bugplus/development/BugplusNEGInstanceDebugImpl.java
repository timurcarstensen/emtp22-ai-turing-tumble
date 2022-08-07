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

/**
 * @Author Christian Bartelt
 * @Date 22.02.22 17:51
 * @Version 0.0.1
 */
final public class BugplusNEGInstanceDebugImpl extends BugplusNEGInstanceImpl implements BugplusNEGInstanceDebug {

    private BugplusInterfaceDebug bugplusIF;


    BugplusNEGInstanceDebugImpl(BugplusImplementation implementation) {

        this.initializeImplementation(this, implementation);

        this.createInterface(1,2);

        this.initializeInterface(this.bugplusIF);

        BugplusControlInPinDebug controlInPin = BugplusControlInPinDebug.getInstance(this);
        this.bugplusIF.setControlInput(controlInPin);
    }


    public BugplusControlInPinDebug getControlIn() {
        return this.bugplusIF.getControlInput();
    }


    public void createInterface(int numDataIn, int numControlOut) {

        this.bugplusIF = BugplusInterfaceDebug.getInstance(numDataIn, numControlOut, this);
    }

    public BugplusInterfaceDebug getInterface() {

        return this.bugplusIF;
    }

    @Override
    public void execute() {
        String id = this.getImplementation().getSpecification().getIdentifier();
        int bit = this.getInterface().getDataInputs().get(0).getVariable().getValue();
        //int summand2 = this.getInterface().getDataInputs().get(1).getVariable().getValue();

        System.out.println("Request: " + id + "(" + bit +  ")");

        super.execute();
    }
}
