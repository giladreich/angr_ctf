# This challenge will be more challenging than the previous challenges that you
# have encountered thus far. Since the goal of this CTF is to teach symbolic
# execution and not how to construct stack frames, these comments will work you
# through understanding what is on the stack.
#   ! ! !
# IMPORTANT: Any addresses in this script aren't necessarily right! Dissassemble
#            the binary yourself to determine the correct addresses!
#   ! ! !

import angr
import claripy
import sys

def main(argv):
  path_to_binary = argv[1]
  project = angr.Project(path_to_binary)

  # For this challenge, we want to begin after the call to scanf. Note that this
  # is in the middle of a function.
  #
  # This challenge requires dealing with the stack, so you have to pay extra
  # careful attention to where you start, otherwise you will enter a condition
  # where the stack is set up incorrectly. In order to determine where after
  # scanf to start, we need to look at the dissassembly of the call and the
  # instruction immediately following it:
  #   sub    $0xc,%esp
  #   lea    -0x18(%ebp),%eax
  #   push   %eax
  #   lea    -0x14(%ebp),%eax
  #   push   %eax
  #   lea    -0xc(%ebp),%eax
  #   push   %eax
  #   lea    -0x10(%ebp),%eax
  #   push   %eax
  #   push   $0x80489c3
  #   call   8048370 <__isoc99_scanf@plt>
  #   add    $0x20,%esp
  # Now, the question is: do we start on the instruction immediately following
  # scanf (add $0x20,%esp), or the instruction following that (not shown)?
  # Consider what the 'add $0x20,%esp' is doing. Hint: it has to do with the
  # scanf parameters that are pushed to the stack before calling the function.
  # Given that we are not calling scanf in our Angr simulation, where should we
  # start?
  # (!)
  start_address = ???
  initial_state = project.factory.blank_state(addr=start_address)

  # We are jumping into the middle of a function! Therefore, we need to account
  # for how the function constructs the stack. The second instruction of the
  # function is:
  #   mov    %esp,%ebp
  # At which point it allocates the part of the stack frame we plan to target:
  #   sub    $0x18,%esp
  # Note the value of esp relative to ebp. The space between them is (usually)
  # the stack space. Since esp was decreased by 0x18
  #
  #        /-------- The stack --------\
  # ebp -> |                           |
  #        |---------------------------|
  #        |                           |
  #        |---------------------------|
  #         . . . (total of 0x18 bytes)
  #         . . . Somewhere in here is
  #         . . . the data that stores
  #         . . . the result of scanf.
  # esp -> |                           |
  #        \---------------------------/
  #
  # Since we are starting after scanf, we are skipping this stack construction
  # step. To make up for this, we need to construct the stack ourselves. Let us
  # start by initializing ebp in the exact same way the program does.
  initial_state.regs.ebp = initial_state.regs.esp

  # scanf("%u %u %u %u") needs to be replaced by injecting four bitvectors. The
  # reason for this is that Angr does not (currently) automatically inject
  # symbols if scanf has more than one input parameter. This means Angr can
  # handle 'scanf("%u")', but not 'scanf("%u %u %u %u")'.
  # You can either copy and paste the line below or use a Python list.
  # (!)
  password0 = claripy.BVS('password0', ???)
  ...

  # Here is the hard part. We need to figure out what the stack looks like, at
  # least well enough to inject our symbols where we want them. In order to do
  # that, let's figure out what the parameters of scanf are:
  #   sub    $0xc,%esp
  #   lea    -0x18(%ebp),%eax
  #   push   %eax
  #   lea    -0x14(%ebp),%eax
  #   push   %eax
  #   lea    -0xc(%ebp),%eax
  #   push   %eax
  #   lea    -0x10(%ebp),%eax
  #   push   %eax
  #   push   $0x80489c3
  #   call   8048370 <__isoc99_scanf@plt>
  # As you can see, the call to scanf looks like this:
  # scanf(  0x80489c3,   ebp - 0x10,   ebp - 0xc,   ebp - 0x14,   ebp - 0x18  )
  #      format_string    password0    password1     password2     password3
  #  From this, we can construct our new, more accurate stack diagram:
  #
  #            /-------- The stack --------\
  # ebp ->     |          padding          |
  #            |---------------------------|
  # ebp - 0x01 |       more padding        |
  #            |---------------------------|
  # ebp - 0x02 |     even more padding     |
  #            |---------------------------|
  #                        . . .               <- How much padding? Hint: how
  #            |---------------------------|      many bytes is password1?
  # ebp - 0x0b |   password1, second byte  |
  #            |---------------------------|
  # ebp - 0x0c |   password1, first byte   |
  #            |---------------------------|
  # ebp - 0x0d |   password0, last byte    |
  #            |---------------------------|
  #                        . . .
  #            |---------------------------|
  # ebp - 0x10 |   password0, first byte   |
  #            |---------------------------|
  #                        . . .
  #            |---------------------------|
  # ebp - 0x14 |   password2, first byte   |
  #            |---------------------------|
  #                        . . .
  #            |---------------------------|
  # ebp - 0x18 |   password3, first byte   |
  #            |---------------------------|
  #                        . . .
  #            |---------------------------|
  # esp ->     |                           |
  #            \---------------------------/
  #
  # Figure out how much space there is and allocate the necessary padding to
  # the stack by decrementing esp before you push the passwords.
  push the password bitvectors.
  padding_length_in_bytes = ???  # :integer
  initial_state.regs.esp -= padding_length_in_bytes

  # Push the variables to the stack. Make sure to push them in the right order!
  # The syntax for the following function is:
  #
  # initial_state.stack_push(bitvector)
  #
  # This will push the bitvector on the stack, and increment esp the correct
  # amount. You will need to push multiple bitvectors on the stack.
  # (!)
  initial_state.stack_push(???)  # :bitvector (claripy.BVS, claripy.BVV, claripy.BV)
  ...

  path_group = project.factory.path_group(initial_state)

  def is_successful(path):
    stdout_output = path.state.posix.dumps(sys.stdout.fileno())
    return ???

  def should_abort(path):
    stdout_output = path.state.posix.dumps(sys.stdout.fileno())
    return ???

  path_group.explore(find=is_successful, avoid=should_abort)

  if path_group.found:
    good_path = path_group.found[0]

    solution0 = good_path.state.se.any_int(password0)
    ...

    solution = ???
    print solution
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)