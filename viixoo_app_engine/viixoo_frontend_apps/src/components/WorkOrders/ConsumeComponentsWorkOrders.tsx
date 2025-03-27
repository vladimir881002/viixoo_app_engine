import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Table,
  Portal,
  Box,
  Checkbox,
} from "@chakra-ui/react"
import useCustomToast from "../../hooks/useCustomToast"
import { useState, useRef } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type ApiError, WorkOrdersService } from "../../client"
import { handleError } from "../../utils"

import type { WorkOrderPublic } from "../../client/types.gen"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"


interface WorkOrderProps {
  item: WorkOrderPublic
}

export const ConsumeComponentsWorkOrders = ({ item }: WorkOrderProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)

  const { showSuccessToast } = useCustomToast()
  const queryClient = useQueryClient()

  // Mutación para actualizar el estado de consumo
  const consumeMutation = useMutation({
    mutationFn: (data: { move_raw_id: number; consumed: boolean }) =>
      WorkOrdersService.consumeComponentWorkorder({ requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] })
      showSuccessToast("Componente actualizado correctamente")
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })


  const handleConsumeChange = (move_raw_id: number, isChecked: boolean) => {
    consumeMutation.mutate({
      move_raw_id: move_raw_id,
      consumed: isChecked
    })
  }
  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
      <Button width="100%" variant="subtle" size="md" colorPalette="gray" >Consumir componente</Button>
      </DialogTrigger>
      <Portal>
      <DialogContent ref={contentRef}>
        <Box as="form">
          <DialogHeader>
            <DialogTitle>Consumir componente</DialogTitle>
          </DialogHeader>
          <DialogBody>
          <Table.Root maxH="150px" size="sm" showColumnBorder>
              <Table.Header>
                <Table.Row>
                  <Table.ColumnHeader fontWeight="bold" w="sm">Componente</Table.ColumnHeader>
                  <Table.ColumnHeader fontWeight="bold" w="sm">Cantidad</Table.ColumnHeader>
                  <Table.ColumnHeader fontWeight="bold" w="sm">Consumido</Table.ColumnHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {item.move_raw_ids?.map((comp) => (
                  <Table.Row key={comp.move_raw_id}>
                    <Table.Cell truncate maxW="sm">
                    {comp.product}
                    </Table.Cell>
                    <Table.Cell truncate maxW="sm">
                    {comp.product_uom_qty}
                    </Table.Cell>
                    <Table.Cell truncate maxW="30%">
                    <Checkbox.Root checked={comp.picked}
                      variant='outline'
                      colorPalette='gray'
                      onCheckedChange={(CheckedChange) => {
                        handleConsumeChange(comp.move_raw_id, !!CheckedChange.checked)
                      }}
                      >
                      <Checkbox.HiddenInput />
                      <Checkbox.Control >
                      <Checkbox.Indicator />
                      </Checkbox.Control >
                    </Checkbox.Root>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table.Root>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                >
                  Cerrar
                </Button>
              </DialogActionTrigger>
            </ButtonGroup>
          </DialogFooter>
        </Box>
        <DialogCloseTrigger />
      </DialogContent>
      </Portal>
    </DialogRoot>
  )
}
