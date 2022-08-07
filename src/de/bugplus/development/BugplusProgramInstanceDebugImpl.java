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
 * @Date 21.02.22 23:44
 * @Version 0.0.1
 */
final public class BugplusProgramInstanceDebugImpl extends BugplusProgramInstanceImpl implements BugplusProgramInstanceDebug {

    final private BugplusBugSetDebug bugs = BugplusBugSetDebug.getInstance();
    private BugplusInterfaceDebug bugplusIF;


    BugplusProgramInstanceDebugImpl(BugplusProgramImplementation implementation) {

        this.setImplementation(implementation);
        this.createInterface(this.getSpecification().getNumDataIn(), this.getSpecification().getNumControlOut());
    }

    protected void createInterface(int numDataIn, int numControlOut) {
        this.bugplusIF = BugplusInterfaceDebug.getInstance(numDataIn, numControlOut, this);
    }

    @Override
    public BugplusControlInPinDebug getControlIn() {
        return this.getInterface().getControlInput();
    }

    @Override
    public void addBug(String bugID, BugplusInstanceDebug bug) {

        this.getBugs().put(bugID, bug);
    }

    @Override
    public BugplusInterfaceDebug getInterface() {
        return this.bugplusIF;
    }

    @Override
    public BugplusBugSetDebug getBugs() {
        return this.bugs;
    }

}
