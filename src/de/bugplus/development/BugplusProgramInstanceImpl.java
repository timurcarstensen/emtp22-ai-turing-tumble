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

import java.util.List;


/**
 * @Author Christian Bartelt
 * @Date 23.01.22 21:37
 * @Version 0.0.1
 */
public class BugplusProgramInstanceImpl extends AbstractBugplusInstance implements BugplusProgramInstance {

    final private BugplusBugSet bugs = BugplusBugSet.getInstance();


    protected BugplusProgramInstanceImpl() {}

    BugplusProgramInstanceImpl(BugplusProgramImplementation implementation) {

        this.setImplementation(implementation);

        this.createInterface(this.getSpecification().getNumDataIn(), this.getSpecification().getNumControlOut());
    }


    @Override
    public void setOutputVariable() {

    }


    @Override
    public void addBug(String bugID, BugplusInstance bug) {

        this.getBugs().put(bugID, bug);
    }

    @Override
    public BugplusBugSet getBugs() {
        return this.bugs;
    }


    public List<BugplusControlOutPin> getControlOutPinsOf(String bugID) {
        return this.getBugs().get(bugID).getControlOuts();
    }

    @Override
    public void unsetPins() {

        for(BugplusDataPin pin : this.getDataInputs()) {
            pin.disconnect();
        }

        this.getDataOut().disconnect();
    }


    @Override
    public void execute() {

        System.out.println("Error: Cannot execute this bug instance because it has not native implementation!");
    }


/*

    @Override
    public void removeNode(String id) {

        //Maybe unnecessary because automatically processed by the garbage collection
        //BugplusInstance nodeToRemove = this.turingNodes.get(id);
        //nodeToRemove.unsetPins();

        this.bugs.remove(id);
    }

    @Override
    public void disconnectDataInPin(String id, int index) {

        BugplusDataInPin pin = this.bugs.get(id).getDataIns().get(index);
        pin.disconnect();
    }

    @Override
    public void disconnectDataOutPin(String id) {

        BugplusDataOutPin pin = this.bugs.get(id).getDataOut();
        pin.disconnect();
    }

    @Override
    public void disconnectControlFlowOut(String idSourceBug, int indexControlOut) {

        BugplusControlOutPin controlOutPin = this.getControlOutPinsOf(idSourceBug).get(indexControlOut);
        controlOutPin.unsetFlowTarget();
    }

*/


}
