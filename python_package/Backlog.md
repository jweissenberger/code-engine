# Backlog

- Check for mailicious code generation like removal of files and print a warning if that's being done
- Determine best temperature value or see if varying it would be better
- write a regex or something to remove any lines of generated code that doesn't start with a tab (which would be code outside of the generated function)
- Can add native support for the most common python package types (pandas, numpy, torch, tf, jax etc) but to accomodate all of them you'll need to figure out the equality function for each of them (since == won't automatically work)
    - could do this by adding an argument as a string_test_case so that someone could submit a test case as "assert tf.is_equal(var1, var2)"
    - Perk: even though you add native support for them you don't actually have to add it as a rec for the python package since you'll just be adding the string equivalent of the equality measure (don't need to import anything)
- split up all of the code that's in code_engine, its getting messy
- add an extra input param for extra packages to use. These could be added as an import statement infront of the function
    - example: use sklearn test-train split to 80-20 split this list (none of the inputs or outputs will be of a sklearn type but you'd still need to import the package)
    - hopefully the model would be able to do it for you but wouldn't hurt to have support for it