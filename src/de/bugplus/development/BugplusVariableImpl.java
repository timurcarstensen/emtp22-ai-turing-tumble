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

import java.util.HashSet;
import java.util.Set;

/**
 * @Author Christian Bartelt
 * @Date 23.01.22 21:37
 * @Version 0.0.1
 */
final class BugplusVariableImpl implements BugplusVariable {

    private int value = 0;

    final private Set<BugplusDataInPin> readers = new HashSet<>();
    final private Set<BugplusDataOutPin> writers = new HashSet<>();


   BugplusVariableImpl() {

       this.value = 0;
    }

    BugplusVariableImpl(int value) {

        this();
        this.value = value;
    }

    BugplusVariableImpl(BugplusDataInPin reader, BugplusDataOutPin writer) {

       this();
       this.readers.add(reader);
       this.writers.add(writer);
       this.value = -1;
    }


    @Override
    public Set<BugplusDataOutPin> getWriters() {
        return this.writers;
    }

    @Override
    public Set<BugplusDataInPin> getReaders() {
        return this.readers;
    }

    @Override
    public void addWriter(BugplusDataOutPin writer) {
        this.writers.add(writer);
    }

    @Override
    public void addReader(BugplusDataInPin reader) {
       this.readers.add(reader);
    }

    @Override
    public void addAllWriters(Set<BugplusDataOutPin> ws) {
       this.writers.addAll(ws);
    }

    @Override
    public void addAllReaders(Set<BugplusDataInPin> rs) {
        this.readers.addAll(rs);
    }

    @Override
    public int getValue() {

        return this.value;
    }

    @Override
    public void setValue(int v) {

        this.value = v;

        for (BugplusDataInPin reader : this.readers) {

            reader.updateInterfaceInputs();
        }
    }
}
