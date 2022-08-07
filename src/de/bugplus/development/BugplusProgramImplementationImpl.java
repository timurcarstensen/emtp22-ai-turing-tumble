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

import de.bugplus.specification.BugplusProgramSpecification;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * @Author Christian Bartelt
 * @Date 03.02.22 22:03
 * @Version 0.0.1
 */
final class BugplusProgramImplementationImpl extends AbstractBugplusProgram implements BugplusProgramImplementation {

    final private List<BugplusStatementNewBug> newBugStatements = new ArrayList<>();
    final private List<BugplusStatementNewFlow> newFlowsStatements = new ArrayList<>();

    final private List<BugplusStatementNewIFConnectDataIn> newIFConnectDataInStatements = new ArrayList<>();
    final private List<BugplusStatementNewIFConnectDataOut> newIFConnectDataOutStatements = new ArrayList<>();

    final private List<BugplusStatementNewIFConnectControlIn> newIFConnectControlInStatements = new ArrayList<>();
    final private List<BugplusStatementNewIFConnectControlOut> newIFConnectControlOutStatements = new ArrayList<>();

    final private Set<BugplusInstance> instances = new HashSet<>();

    private boolean debugMode = false;


    private BugplusProgramImplementationImpl() {
    }

    public BugplusProgramImplementationImpl(BugplusProgramSpecification specification) {

        this.specification = specification;
        this.debugMode = false;
    }


    @Override
    public void addBug(String specID, String bugID) {

        this.newBugStatements.add(BugplusStatementNewBug.getInstance(specID, bugID));
    }

    //Tobi
    @Override
    public Set<BugplusInstance> getBugs() {
        return this.instances;
    }

    @Override
    public void removeNode(String id) {

        // implement
    }

    @Override
    public void addDataFlow(String idSourceBug, String idTargetBug, int indexDataIn) {

        this.newFlowsStatements.add(BugplusStatementNewFlowData.getInstance(idSourceBug, idTargetBug, indexDataIn));
    }

    @Override
    public void disconnectDataInPin(String idDataIn, int index) {
        // implement
    }

    @Override
    public void disconnectDataOutPin(String idDataOut) {
        // implement
    }

    @Override
    public void addControlFlow(String idSourceBug, int indexControlOut, String idTargetBug) {

        this.newFlowsStatements.add(BugplusStatementNewFlowControl.getInstance(idSourceBug, indexControlOut, idTargetBug));
    }

    @Override
    public void disconnectControlFlowOut(String idSourceBug, int indexControlOut) {
        // implement
    }

    @Override
    public void connectDataInInterface(String idInternalBug, int indexInternalDataIn, int indexExternalDataInIF) {

        this.newIFConnectDataInStatements.add(BugplusStatementNewIFConnectDataIn.getInstance(idInternalBug, indexInternalDataIn, indexExternalDataInIF));
    }

    @Override
    public void connectDataOutInterface(String idInternalBug) {

        this.newIFConnectDataOutStatements.add(BugplusStatementNewIFConnectDataOut.getInstance(idInternalBug));
    }

    @Override
    public void connectControlInInterface(String idInternalBug) {

        this.newIFConnectControlInStatements.add(BugplusStatementNewIFConnectControlIn.getInstance(idInternalBug));
    }

    @Override
    public void connectControlOutInterface(String idInternalBug, int indexInternalControlOut, int indexExternalControlOutIF) {

        this.newIFConnectControlOutStatements.add(BugplusStatementNewIFConnectControlOut.getInstance(idInternalBug, indexInternalControlOut, indexExternalControlOutIF));
    }


    @Override
    public BugplusProgramInstance instantiate() {

        BugplusProgramInstance newInstance = BugplusProgramInstance.getInstance(this);

        for (BugplusStatementNewBug newBugStatement : this.newBugStatements) {
            newBugStatement.apply(newInstance);
        }

        this.instanciateInternals(newInstance);

        for (BugplusStatementNewIFConnectControlIn newIFConnectControlInStatement : this.newIFConnectControlInStatements) {
            newIFConnectControlInStatement.apply(newInstance);
        }

        return newInstance;
    }

    @Override
    public BugplusProgramInstanceDebug instantiateDebug() {

        this.debugMode = true;

        BugplusProgramInstanceDebug newInstance = BugplusProgramInstanceDebug.getInstance(this);

        for (BugplusStatementNewBug newBugStatement : this.newBugStatements) {
            BugplusStatementNewBugDebug newBugStatementDebug = BugplusStatementNewBugDebug.getInstance(newBugStatement.getSpecificationID(), newBugStatement.getBugRoleID());
            newBugStatementDebug.apply(newInstance);
        }

        this.instanciateInternals(newInstance);

        for (BugplusStatementNewIFConnectControlIn newIFConnectControlInStatement : this.newIFConnectControlInStatements) {
            BugplusStatementNewIFConnectControlInDebug newIFConnectControlInStatementDebug = BugplusStatementNewIFConnectControlInDebug.getInstance(newIFConnectControlInStatement.getInternalBugID());
            newIFConnectControlInStatementDebug.apply(newInstance);
        }

        return newInstance;
    }


    private BugplusProgramInstance instanciateInternals(BugplusProgramInstance instance) {

        this.instances.add(instance);


        for (BugplusStatementNewFlow newFlowStatement : this.newFlowsStatements) {
            newFlowStatement.apply(instance);
        }

        for (BugplusStatementNewIFConnectDataIn newIFConnectDataInStatement : this.newIFConnectDataInStatements) {
            newIFConnectDataInStatement.apply(instance);
        }

        for (BugplusStatementNewIFConnectDataOut newIFConnectDataOutStatement : this.newIFConnectDataOutStatements) {
            newIFConnectDataOutStatement.apply(instance);
        }

        for (BugplusStatementNewIFConnectControlOut newIFConnectControlOutStatement : this.newIFConnectControlOutStatements) {
            newIFConnectControlOutStatement.apply(instance);
        }

        return instance;
    }

}
